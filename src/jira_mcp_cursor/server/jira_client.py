"""Jira API client for interacting with Jira REST API."""

import httpx
from typing import Any, Optional
import logging
import asyncio

from .exceptions import (
    JiraAPIError,
    AuthenticationError,
    RateLimitError,
    TicketNotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class JiraClient:
    """Async client for Jira REST API with automatic retry logic.

    Attributes:
        base_url: Jira instance URL
        auth: Authentication credentials (email/token or username/password)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts for failed requests
    """

    def __init__(
        self, base_url: str, auth: tuple[str, str], timeout: int = 30, max_retries: int = 3
    ):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout
        self.max_retries = max_retries

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> dict[str, Any]:
        """Make authenticated request to Jira API with retry logic.

        Implements exponential backoff for rate limits (429) and network errors.
        Retries up to self.max_retries times with delays of 1s, 2s, 4s, etc.

        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint path (e.g., '/issue/PROJ-123')
            params: Query parameters
            json: JSON body for POST/PUT requests
            retry_count: Current retry attempt (internal, starts at 0)

        Returns:
            JSON response from Jira API

        Raises:
            AuthenticationError: On 401 responses
            RateLimitError: On 429 responses (after max retries)
            TicketNotFoundError: On 404 responses
            ValidationError: On 400 responses
            JiraAPIError: On other errors
        """
        url = f"{self.base_url}/rest/api/2{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    auth=self.auth,
                    params=params,
                    json=json,
                    timeout=self.timeout,
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                return response.json() if response.content else {}

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                error_text = e.response.text
                logger.error(f"HTTP error: {status_code}")

                # Map status codes to specific exceptions
                if status_code == 401:
                    raise AuthenticationError(
                        "Authentication failed. Check your credentials.",
                        status_code=status_code,
                        details=error_text,
                    )
                elif status_code == 404:
                    raise TicketNotFoundError(
                        "Ticket not found or you don't have permission to view it.",
                        status_code=status_code,
                        details=error_text,
                    )
                elif status_code == 400:
                    raise ValidationError(
                        "Invalid request. Check your parameters.",
                        status_code=status_code,
                        details=error_text,
                    )
                elif status_code == 429:
                    # Rate limit - retry with exponential backoff
                    if retry_count < self.max_retries:
                        wait_time = 2**retry_count  # 1s, 2s, 4s
                        logger.warning(
                            f"Rate limit hit on {endpoint}. Retrying in {wait_time}s (attempt {retry_count + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        return await self._request(
                            method,
                            endpoint,
                            params,
                            json,
                            retry_count=retry_count + 1,
                        )
                    else:
                        raise RateLimitError(
                            "Rate limit exceeded. Please try again later.",
                            status_code=status_code,
                            details=error_text,
                        )
                else:
                    raise JiraAPIError(
                        f"Jira API error: {status_code}",
                        status_code=status_code,
                        details=error_text,
                    )

            except httpx.RequestError as e:
                # Network errors - retry
                if retry_count < self.max_retries and isinstance(
                    e, (httpx.ConnectError, httpx.TimeoutException)
                ):
                    wait_time = 2**retry_count
                    logger.warning(
                        f"Network error on {endpoint}: {type(e).__name__}. Retrying in {wait_time}s (attempt {retry_count + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method,
                        endpoint,
                        params,
                        json,
                        retry_count=retry_count + 1,
                    )
                else:
                    logger.error(f"Request error: {str(e)}")
                    raise JiraAPIError(f"Request failed: {str(e)}")

    async def _get_board_id(self) -> Optional[int]:
        """Get the first available board ID for fallback queries.

        Returns:
            Board ID if found, None otherwise
        """
        try:
            # Note: agile API uses /rest/agile prefix, not /rest/api
            url = f"{self.base_url}/rest/agile/1.0/board"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    auth=self.auth,
                    params={"maxResults": 1},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                result = response.json()

            boards = result.get("values", [])
            if boards:
                logger.info(
                    f"Found board for fallback: {boards[0]['name']} (ID: {boards[0]['id']})"
                )
                return boards[0]["id"]
            return None
        except Exception as e:
            logger.warning(f"Could not get board ID: {e}")
            return None

    async def _search_via_agile_api(
        self,
        jql: str,
        fields: Optional[list[str]] = None,
        max_results: int = 50,
    ) -> dict[str, Any]:
        """Search for issues using Agile Board API as fallback.

        This is used when the standard /search endpoint is unavailable (410).
        Searches across all accessible boards and aggregates results.

        Args:
            jql: JQL query string
            fields: Fields to include (not fully supported in agile API)
            max_results: Maximum results to return

        Returns:
            Response in same format as standard search
        """
        logger.info(f"Using agile board API fallback with JQL: {jql}")

        # Get all accessible boards
        try:
            url = f"{self.base_url}/rest/agile/1.0/board"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    auth=self.auth,
                    params={"maxResults": 50},  # Get up to 50 boards
                    timeout=self.timeout,
                )
                response.raise_for_status()
                boards_result = response.json()

            boards = boards_result.get("values", [])
            logger.info(f"Found {len(boards)} accessible boards")

            if not boards:
                logger.error("No boards found for agile API fallback")
                return {"issues": [], "total": 0}

            # Search across all boards and aggregate results
            all_issues = []
            seen_keys = set()

            for board in boards[:10]:  # Limit to first 10 boards to avoid too many API calls
                board_id = board["id"]
                board_name = board["name"]

                try:
                    url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/issue"
                    params: dict[str, Any] = {
                        "jql": jql,
                        "maxResults": max_results,
                    }
                    if fields:
                        params["fields"] = ",".join(fields)

                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            url,
                            auth=self.auth,
                            params=params,
                            timeout=self.timeout,
                        )
                        response.raise_for_status()
                        result = response.json()

                    # Add unique issues (avoid duplicates across boards)
                    for issue in result.get("issues", []):
                        issue_key = issue.get("key")
                        if issue_key and issue_key not in seen_keys:
                            all_issues.append(issue)
                            seen_keys.add(issue_key)

                            # Stop if we hit max_results
                            if len(all_issues) >= max_results:
                                break

                    if len(all_issues) >= max_results:
                        break

                except Exception as board_error:
                    logger.debug(f"Could not search board {board_name}: {board_error}")
                    continue

            return {
                "issues": all_issues[:max_results],
                "total": len(all_issues),
            }

        except Exception as e:
            logger.error(f"Agile API fallback failed: {e}")
            return {"issues": [], "total": 0}

    async def search_issues(
        self,
        jql: str,
        fields: Optional[list[str]] = None,
        max_results: int = 50,
    ) -> dict[str, Any]:
        """Search for issues using JQL.

        Automatically falls back to agile board API if standard search
        endpoint is unavailable (HTTP 410).

        Args:
            jql: JQL query string
            fields: Fields to include in response
            max_results: Maximum results to return

        Returns:
            Dict with 'issues' list and 'total' count
        """
        params: dict[str, Any] = {
            "jql": jql,
            "maxResults": max_results,
        }
        if fields:
            params["fields"] = ",".join(fields)

        logger.info(f"Searching issues with JQL: {jql}")

        try:
            return await self._request("GET", "/search", params=params)
        except JiraAPIError as e:
            # If search endpoint is gone (410), try agile board API fallback
            if e.status_code == 410:
                logger.warning(
                    "Standard search endpoint unavailable (410), using agile board API fallback"
                )
                try:
                    return await self._search_via_agile_api(jql, fields, max_results)
                except Exception as fallback_error:
                    logger.error(f"Agile API fallback also failed: {fallback_error}")
                    raise JiraAPIError(
                        "Unable to search issues. Both standard and agile APIs failed. "
                        "Please check your Jira permissions.",
                        status_code=410,
                    )
            raise

    async def get_issue(
        self,
        issue_key: str,
        fields: Optional[list[str]] = None,
        expand: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Get a single issue by key."""
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = ",".join(fields)
        if expand:
            params["expand"] = ",".join(expand)

        logger.info(f"Fetching issue: {issue_key}")
        return await self._request("GET", f"/issue/{issue_key}", params=params)

    async def update_issue(
        self,
        issue_key: str,
        fields: dict[str, Any],
    ) -> None:
        """Update issue fields."""
        logger.info(f"Updating issue: {issue_key}")
        await self._request(
            "PUT",
            f"/issue/{issue_key}",
            json={"fields": fields},
        )

    async def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
        """Get available transitions for an issue."""
        result = await self._request("GET", f"/issue/{issue_key}/transitions")
        return result.get("transitions", [])

    async def transition_issue(
        self,
        issue_key: str,
        transition_id: str,
        comment: Optional[str] = None,
    ) -> None:
        """Transition issue to new status."""
        payload: dict[str, Any] = {"transition": {"id": transition_id}}
        if comment:
            payload["update"] = {"comment": [{"add": {"body": comment}}]}

        logger.info(f"Transitioning issue {issue_key} to transition {transition_id}")
        await self._request("POST", f"/issue/{issue_key}/transitions", json=payload)

    async def add_comment(
        self,
        issue_key: str,
        comment: str,
    ) -> dict[str, Any]:
        """Add comment to an issue."""
        logger.info(f"Adding comment to issue: {issue_key}")
        return await self._request(
            "POST",
            f"/issue/{issue_key}/comment",
            json={"body": comment},
        )
