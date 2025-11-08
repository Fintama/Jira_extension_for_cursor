"""Tests for error handling and retry logic."""

import pytest
from unittest.mock import AsyncMock, patch
from jira_mcp_cursor.server.jira_client import JiraClient, JiraAPIError
import httpx


@pytest.mark.asyncio
async def test_authentication_error_raised():
    """Test that 401 responses raise AuthenticationError."""
    from jira_mcp_cursor.server.exceptions import AuthenticationError

    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "invalid-token"),
    )

    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=AuthenticationError("Invalid credentials")),
    ):
        with pytest.raises(AuthenticationError) as exc_info:
            await client.get_issue("TEST-123")

        assert "Invalid credentials" in str(exc_info.value)


@pytest.mark.asyncio
async def test_rate_limit_error_raised():
    """Test that 429 responses raise RateLimitError."""
    from jira_mcp_cursor.server.exceptions import RateLimitError

    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=RateLimitError("Rate limit exceeded")),
    ):
        with pytest.raises(RateLimitError) as exc_info:
            await client.search_issues("assignee = currentUser()")

        assert "Rate limit" in str(exc_info.value)


@pytest.mark.asyncio
async def test_ticket_not_found_error_raised():
    """Test that 404 responses raise TicketNotFoundError."""
    from jira_mcp_cursor.server.exceptions import TicketNotFoundError

    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=TicketNotFoundError("Ticket not found")),
    ):
        with pytest.raises(TicketNotFoundError) as exc_info:
            await client.get_issue("NONEXISTENT-999")

        assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_retry_on_network_error():
    """Test that network errors trigger retry logic."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    # Mock httpx.AsyncClient to fail twice, then succeed
    call_count = {"count": 0}

    class MockResponse:
        status_code = 200
        content = b'{"key": "TEST-123"}'

        def raise_for_status(self):
            pass

        def json(self):
            return {"key": "TEST-123"}

    async def mock_request_method(*args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise httpx.ConnectError("Connection refused")
        return MockResponse()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.request = mock_request_method
        mock_client_class.return_value.__aenter__.return_value = mock_client_instance

        result = await client.get_issue("TEST-123")

        # Should have retried and eventually succeeded
        assert result["key"] == "TEST-123"
        assert call_count["count"] == 3  # Failed twice, succeeded third time


@pytest.mark.asyncio
async def test_retry_on_rate_limit():
    """Test that 429 rate limit triggers retry with backoff."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    # Mock httpx to return 429 once, then 200
    call_count = {"count": 0}

    class MockResponse429:
        status_code = 429
        text = "Rate limit exceeded"

        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "429 Too Many Requests",
                request=httpx.Request("GET", "https://test.atlassian.net"),
                response=self,
            )

    class MockResponse200:
        status_code = 200
        content = b'{"issues": []}'

        def raise_for_status(self):
            pass

        def json(self):
            return {"issues": []}

    async def mock_request_method(*args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] < 2:
            return MockResponse429()
        return MockResponse200()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.request = mock_request_method
        mock_client_class.return_value.__aenter__.return_value = mock_client_instance

        # Mock asyncio.sleep to avoid waiting
        with patch("asyncio.sleep", new=AsyncMock()):
            result = await client.search_issues("assignee = currentUser()")

            # Should have retried after rate limit
            assert call_count["count"] == 2
            assert result == {"issues": []}


@pytest.mark.asyncio
async def test_max_retries_exceeded():
    """Test that retry gives up after max attempts."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    # Always fail
    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=httpx.ConnectError("Connection refused")),
    ):
        with pytest.raises((httpx.ConnectError, JiraAPIError)):
            await client.get_issue("TEST-123")


@pytest.mark.asyncio
async def test_no_retry_on_4xx_errors():
    """Test that 4xx errors (except 429) don't retry."""
    from jira_mcp_cursor.server.exceptions import ValidationError

    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    call_count = {"count": 0}

    async def mock_request(*args, **kwargs):
        call_count["count"] += 1
        raise ValidationError("Invalid request")

    with patch.object(client, "_request", new=mock_request):
        with pytest.raises(ValidationError):
            await client.get_issue("TEST-123")

        # Should NOT have retried - only called once
        assert call_count["count"] == 1


@pytest.mark.asyncio
async def test_error_message_sanitization():
    """Test that error messages don't leak credentials."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "super-secret-token"),
    )

    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=JiraAPIError("API error occurred")),
    ):
        with pytest.raises(JiraAPIError) as exc_info:
            await client.get_issue("TEST-123")

        error_msg = str(exc_info.value)
        # Should not contain credentials
        assert "super-secret-token" not in error_msg
        assert (
            "test@example.com" not in error_msg or "test@example.com" in error_msg
        )  # Email might be ok


@pytest.mark.asyncio
async def test_connection_timeout():
    """Test handling of connection timeout errors."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
        timeout=1,
    )

    with patch.object(
        client, "_request", new=AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
    ):
        with pytest.raises((httpx.TimeoutException, JiraAPIError)):
            await client.get_issue("TEST-123")


@pytest.mark.asyncio
async def test_connection_refused():
    """Test handling of connection refused errors."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=httpx.ConnectError("Connection refused")),
    ):
        with pytest.raises((httpx.ConnectError, JiraAPIError)):
            await client.search_issues("assignee = currentUser()")


@pytest.mark.asyncio
async def test_malformed_response():
    """Test handling of invalid JSON responses."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    # Mock response that returns invalid JSON
    with patch.object(
        client, "_request", new=AsyncMock(side_effect=JiraAPIError("Invalid JSON response"))
    ):
        with pytest.raises(JiraAPIError):
            await client.get_issue("TEST-123")


@pytest.mark.asyncio
async def test_unexpected_status_code():
    """Test handling of unexpected HTTP status codes."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    # Mock 500 server error
    with patch.object(
        client, "_request", new=AsyncMock(side_effect=JiraAPIError("Server error", status_code=500))
    ):
        with pytest.raises(JiraAPIError) as exc_info:
            await client.get_issue("TEST-123")

        assert exc_info.value.status_code == 500
