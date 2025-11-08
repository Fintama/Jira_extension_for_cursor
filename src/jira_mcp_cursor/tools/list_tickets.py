"""List tickets tool."""

from mcp.types import Tool, TextContent
from ..server.jira_client import JiraClient
from ..utils.jql_builder import build_my_tickets_jql
from ..utils.ticket_parser import parse_ticket_summary
import json


async def handle_list_my_tickets(
    arguments: dict,
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle list_my_tickets tool call."""
    # Build JQL query
    jql = build_my_tickets_jql(
        status=arguments.get("status"),
        project=arguments.get("project"),
    )

    # Search issues
    result = await jira_client.search_issues(
        jql=jql,
        max_results=arguments.get("max_results", 50),
        fields=["summary", "status", "priority", "assignee", "created", "updated"],
    )

    # Parse results
    tickets = [parse_ticket_summary(issue) for issue in result.get("issues", [])]

    response = {
        "tickets": tickets,
        "total": result.get("total", 0),
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


# Tool definition
LIST_MY_TICKETS_TOOL = Tool(
    name="list_my_tickets",
    description="List all tickets assigned to the current user",
    inputSchema={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by status (e.g., 'In Progress', 'To Do')",
            },
            "project": {
                "type": "string",
                "description": "Filter by project key",
            },
            "max_results": {
                "type": "number",
                "description": "Maximum number of results",
                "default": 50,
            },
        },
    },
)
