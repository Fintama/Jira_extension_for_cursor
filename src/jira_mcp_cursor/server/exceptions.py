"""Custom exceptions for Jira MCP Server.

This module provides a hierarchy of exceptions for different error scenarios
when interacting with the Jira API. Each exception maps to specific HTTP status
codes or error conditions.
"""

from typing import Optional


class JiraAPIError(Exception):
    """Base exception for Jira API errors.

    All Jira-related exceptions inherit from this class. It captures
    the HTTP status code and additional error details from the API response.

    Attributes:
        status_code: HTTP status code from Jira API (if applicable)
        details: Additional error details from API response

    Example:
        >>> raise JiraAPIError("Something went wrong", status_code=500)
    """

    def __init__(
        self, message: str, status_code: Optional[int] = None, details: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class AuthenticationError(JiraAPIError):
    """Raised when authentication fails (HTTP 401).

    This error indicates invalid credentials (email/token or username/password).

    Common causes:
    - Expired API token
    - Incorrect email address
    - Invalid password
    - Insufficient permissions

    Example:
        >>> raise AuthenticationError("Invalid credentials", status_code=401)

    Resolution:
        - Verify credentials in .env file
        - Generate a new API token at https://id.atlassian.com/manage-profile/security/api-tokens
        - Check that email matches Jira account
    """

    pass


class RateLimitError(JiraAPIError):
    """Raised when API rate limit is exceeded (HTTP 429).

    Jira Cloud has rate limits (typically 10-25 requests/second per user).
    The client will automatically retry with exponential backoff.

    Example:
        >>> raise RateLimitError("Rate limit exceeded", status_code=429)

    Resolution:
        - Wait and retry (automatic with backoff)
        - Reduce request frequency
        - Consider caching frequently accessed data
        - Upgrade Jira plan for higher limits
    """

    pass


class TicketNotFoundError(JiraAPIError):
    """Raised when ticket is not found (HTTP 404).

    This error means the ticket doesn't exist or you don't have permission to view it.

    Common causes:
    - Ticket key doesn't exist
    - Ticket was deleted
    - Insufficient view permissions
    - Wrong Jira instance

    Example:
        >>> raise TicketNotFoundError("Ticket PROJ-999 not found", status_code=404)

    Resolution:
        - Verify ticket key is correct (format: ABC-123)
        - Check you have permission to view the ticket
        - Confirm you're connected to the correct Jira instance
    """

    pass


class ValidationError(JiraAPIError):
    """Raised when input validation fails (HTTP 400).

    This error indicates malformed requests or invalid parameters.

    Common causes:
    - Invalid JQL syntax
    - Missing required fields
    - Invalid field values
    - Malformed JSON

    Example:
        >>> raise ValidationError("Invalid JQL query", status_code=400)

    Resolution:
        - Check input parameters
        - Verify JQL syntax
        - Ensure all required fields are provided
    """

    pass


class TransitionError(JiraAPIError):
    """Raised when status transition is invalid.

    This error occurs when trying to transition a ticket to a status
    that is not available from the current state.

    Common causes:
    - Target status not in workflow
    - Workflow doesn't allow this transition
    - Insufficient permissions for transition

    Example:
        >>> raise TransitionError("Cannot transition from 'To Do' to 'Closed'")

    Resolution:
        - Use get_transitions() to see available transitions
        - Check workflow configuration in Jira
        - Verify you have permission to perform this transition
    """

    pass
