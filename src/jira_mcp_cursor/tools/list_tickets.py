"""List tickets tools — my tickets and generic listing with fuzzy type resolution."""

import json
from typing import Any

from mcp.types import Tool, TextContent

from ..server.jira_client import JiraClient
from ..utils.jql_builder import build_my_tickets_jql
from ..utils.ticket_parser import parse_ticket_summary


async def handle_list_my_tickets(
    arguments: dict,
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle list_my_tickets tool call."""
    from ..config.settings import Settings

    settings = Settings()

    # Use provided project or fall back to default
    project = arguments.get("project")
    if not project and settings.jira_project_key:
        project = settings.jira_project_key

    # Build JQL query
    jql = build_my_tickets_jql(
        status=arguments.get("status"),
        project=project,
    )

    # Search issues
    result = await jira_client.search_issues(
        jql=jql,
        max_results=arguments.get("max_results", 50),
        fields=["summary", "status", "priority", "assignee", "created", "updated"],
    )

    tickets = [parse_ticket_summary(issue) for issue in result.get("issues", [])]

    response = {
        "tickets": tickets,
        "total": result.get("total", 0),
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_list_tickets(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle list_tickets tool call."""
    from ..config.settings import Settings

    settings = Settings()

    project = arguments.get("project")
    if not project:
        project = settings.jira_project_key
        if not project:
            raise ValueError(
                "No project specified and no default project configured. "
                "Please specify a project or set JIRA_PROJECT_KEY."
            )

    issue_type = arguments.get("issue_type")
    resolved_type: str | None = None

    if issue_type:
        resolved_type = await jira_client.resolve_issue_type(issue_type, project)

    jql_parts: list[str] = []

    if resolved_type:
        jql_parts.append(f'issuetype = "{resolved_type}"')

    jql_parts.append(f'project = "{project}"')

    if status := arguments.get("status"):
        jql_parts.append(f'status = "{status}"')

    jql = " AND ".join(jql_parts) + " ORDER BY updated DESC"

    result = await jira_client.search_issues(
        jql=jql,
        max_results=arguments.get("max_results", 50),
        fields=["summary", "status", "priority", "assignee", "issuetype", "created", "updated"],
    )

    issues = [parse_ticket_summary(issue) for issue in result.get("issues", [])]

    response: dict[str, Any] = {
        "issues": issues,
        "total": result.get("total", 0),
    }
    if resolved_type:
        response["resolved_type"] = resolved_type

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


LIST_MY_TICKETS_TOOL = Tool(
    name="list_my_tickets",
    description="List all tickets assigned to the current user. Defaults to configured project if set.",
    inputSchema={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by status (e.g., 'In Progress', 'To Do')",
            },
            "project": {
                "type": "string",
                "description": "Filter by project key (optional, uses default project from config if not specified)",
            },
            "max_results": {
                "type": "number",
                "description": "Maximum number of results",
                "default": 50,
            },
        },
    },
)

LIST_TICKETS_TOOL = Tool(
    name="list_tickets",
    description=(
        "List tickets in a Jira project, optionally filtered by issue type. "
        "The issue type is resolved dynamically against the project's configured types "
        "using fuzzy matching (e.g. 'epic' resolves to 'Program epic' if that's what "
        "the project uses). Omit issue_type to list all tickets."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "project": {
                "type": "string",
                "description": (
                    "Project key (optional, uses default project from config if not specified)"
                ),
            },
            "issue_type": {
                "type": "string",
                "description": (
                    "Filter by issue type (e.g. 'Epic', 'Story', 'Bug'). "
                    "Resolved dynamically against the project's configured types."
                ),
            },
            "status": {
                "type": "string",
                "description": "Filter by status (e.g., 'In Progress', 'To Do')",
            },
            "max_results": {
                "type": "number",
                "description": "Maximum number of results",
                "default": 50,
            },
        },
    },
)
