"""Get ticket tool."""

from mcp.types import Tool, TextContent
from ..server.jira_client import JiraClient
from ..utils.ticket_parser import parse_ticket_detail
import json


async def handle_get_ticket(
    arguments: dict,
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle get_ticket tool call."""
    ticket_key = arguments["ticket_key"]

    # Determine fields to expand
    expand = []
    if arguments.get("include_comments", True):
        expand.append("renderedFields")

    # Fetch issue
    issue = await jira_client.get_issue(
        issue_key=ticket_key,
        expand=expand if expand else None,
    )

    # Parse ticket
    ticket = parse_ticket_detail(issue)

    return [TextContent(type="text", text=json.dumps(ticket, indent=2))]


async def handle_get_highest_priority_ticket(
    arguments: dict,
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle get_highest_priority_ticket tool call.

    Args:
        arguments: Tool arguments including optional project and exclude_status
        jira_client: Jira API client instance

    Returns:
        List of TextContent with highest priority ticket details or error
    """
    from ..utils.jql_builder import build_highest_priority_jql
    from ..config.settings import Settings

    settings = Settings()

    # Use provided project or fall back to default
    project = arguments.get("project")
    if not project and settings.jira_project_key:
        project = settings.jira_project_key

    # Validate and normalize exclude_status parameter
    exclude_status = arguments.get("exclude_status")
    if exclude_status is not None:
        # Convert single string to list for consistency
        if isinstance(exclude_status, str):
            exclude_status = [exclude_status]
        elif not isinstance(exclude_status, list):
            exclude_status = None  # Ignore invalid types

    # Build JQL query for highest priority ticket
    jql = build_highest_priority_jql(
        project=project,
        exclude_statuses=exclude_status,
    )

    # Search for highest priority ticket (limit to 1)
    result = await jira_client.search_issues(
        jql=jql,
        max_results=1,
    )

    # If no tickets found, return empty result
    if not result.get("issues"):
        return [TextContent(type="text", text=json.dumps({"error": "No tickets found"}, indent=2))]

    # Parse and return the highest priority ticket detail
    ticket = parse_ticket_detail(result["issues"][0])

    return [TextContent(type="text", text=json.dumps(ticket, indent=2))]


# Tool definitions
GET_TICKET_TOOL = Tool(
    name="get_ticket",
    description="Get detailed information about a specific ticket",
    inputSchema={
        "type": "object",
        "properties": {
            "ticket_key": {
                "type": "string",
                "description": "Jira ticket key (e.g., 'PROJ-123')",
            },
            "include_comments": {
                "type": "boolean",
                "description": "Include comments in response",
                "default": True,
            },
        },
        "required": ["ticket_key"],
    },
)

GET_HIGHEST_PRIORITY_TICKET_TOOL = Tool(
    name="get_highest_priority_ticket",
    description="Get the highest priority ticket assigned to the current user. Defaults to configured project if set.",
    inputSchema={
        "type": "object",
        "properties": {
            "exclude_status": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Statuses to exclude",
            },
            "project": {
                "type": "string",
                "description": "Filter by project key (optional, uses default project from config if not specified)",
            },
        },
    },
)
