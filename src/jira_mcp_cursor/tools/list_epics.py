"""List epics tool — discovers epic issue types dynamically via fuzzy name matching."""

from mcp.types import Tool, TextContent
from ..server.jira_client import JiraClient
from ..utils.jql_builder import build_epics_jql
from ..utils.ticket_parser import parse_ticket_summary
import json


async def handle_list_epics(
    arguments: dict,
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle list_epics tool call.

    1. Queries the Jira instance for all issue types containing 'epic'.
    2. Searches for matching issues using the discovered types.
    """
    from ..config.settings import Settings

    settings = Settings()

    project = arguments.get("project")
    if not project and settings.jira_project_key:
        project = settings.jira_project_key

    epic_types = await jira_client.get_epic_issue_types()

    if not epic_types:
        response = {
            "epics": [],
            "total": 0,
            "epic_types_found": [],
        }
        return [TextContent(type="text", text=json.dumps(response, indent=2))]

    jql = build_epics_jql(
        epic_type_names=epic_types,
        project=project,
        status=arguments.get("status"),
    )

    result = await jira_client.search_issues(
        jql=jql,
        max_results=arguments.get("max_results", 50),
        fields=["summary", "status", "priority", "assignee", "issuetype", "created", "updated"],
    )

    epics = [parse_ticket_summary(issue) for issue in result.get("issues", [])]

    response = {
        "epics": epics,
        "total": result.get("total", 0),
        "epic_types_found": epic_types,
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


LIST_EPICS_TOOL = Tool(
    name="list_epics",
    description=(
        "List epics in the Jira project. Automatically discovers all epic-level issue types "
        "(e.g. Epic, Program Epic) configured on the instance via fuzzy name matching."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "project": {
                "type": "string",
                "description": (
                    "Project key to list epics from "
                    "(optional, uses default project from config if not specified)"
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
