"""Create ticket tools."""

from typing import Any
from mcp.types import Tool, TextContent
from ..server.jira_client import JiraClient
import json


# Tool Definitions
CREATE_ISSUE_TOOL = Tool(
    name="create_issue",
    description="""Create a new Jira issue (Story, Task, Bug, etc.).

Use this to create stories under a feature/epic, or standalone tasks.

Example uses:
- Create a story under an epic for implementation phases
- Create a task for a specific piece of work
- Create a bug report

If project_key is not specified, uses the default project from configuration.""",
    inputSchema={
        "type": "object",
        "properties": {
            "project_key": {
                "type": "string",
                "description": "Project key (e.g., 'SWI', 'PROJ'). Optional if default project is configured.",
            },
            "summary": {
                "type": "string",
                "description": "Issue title/summary",
            },
            "description": {
                "type": "string",
                "description": "Detailed description of the issue",
            },
            "issue_type": {
                "type": "string",
                "description": "Type of issue: Task, Story, Bug, Epic (default: Task)",
                "default": "Task",
            },
            "priority": {
                "type": "string",
                "description": "Priority: Highest, High, Medium, Low, Lowest (optional)",
            },
            "assignee": {
                "type": "string",
                "description": "Account ID or email of assignee (optional)",
            },
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of labels (optional)",
            },
            "parent_key": {
                "type": "string",
                "description": "Parent issue key for creating stories under epics (optional)",
            },
        },
        "required": ["summary", "description"],
    },
)

CREATE_SUBTASK_TOOL = Tool(
    name="create_subtask",
    description="""Create a subtask under a parent issue.

Use this to break down stories into implementation subtasks.

Example: Breaking down "Story: Auth Backend" into:
- Subtask: Database schema
- Subtask: API endpoints
- Subtask: Unit tests""",
    inputSchema={
        "type": "object",
        "properties": {
            "parent_key": {
                "type": "string",
                "description": "Parent issue key (e.g., 'SWI-501')",
            },
            "summary": {
                "type": "string",
                "description": "Subtask title/summary",
            },
            "description": {
                "type": "string",
                "description": "Detailed description of the subtask",
            },
            "assignee": {
                "type": "string",
                "description": "Account ID or email of assignee (optional)",
            },
            "priority": {
                "type": "string",
                "description": "Priority: Highest, High, Medium, Low, Lowest (optional)",
            },
        },
        "required": ["parent_key", "summary", "description"],
    },
)

GET_SUBTASKS_TOOL = Tool(
    name="get_subtasks",
    description="""Get all subtasks of a parent issue.

Use this to view existing subtasks before adding more or to check progress.""",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_key": {
                "type": "string",
                "description": "Parent issue key (e.g., 'SWI-501')",
            },
        },
        "required": ["issue_key"],
    },
)

ASSIGN_ISSUE_TOOL = Tool(
    name="assign_issue",
    description="""Assign an issue to a user.

Use this to assign tickets to team members.""",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_key": {
                "type": "string",
                "description": "Issue key (e.g., 'SWI-501')",
            },
            "assignee": {
                "type": "string",
                "description": "Account ID or email of assignee. Use '-1' for automatic, 'null' for unassigned",
            },
        },
        "required": ["issue_key", "assignee"],
    },
)


# Handlers
async def handle_create_issue(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle create_issue tool call."""
    from ..config.settings import Settings

    settings = Settings()

    # Use provided project_key or fall back to default
    project_key = arguments.get("project_key")
    if not project_key:
        project_key = settings.jira_project_key
        if not project_key:
            raise ValueError(
                "No project_key provided and no default project configured. "
                "Please specify project_key or set JIRA_PROJECT_KEY in configuration."
            )

    summary = arguments["summary"]
    description = arguments["description"]
    issue_type = arguments.get("issue_type", "Task")
    priority = arguments.get("priority")
    assignee = arguments.get("assignee")
    labels = arguments.get("labels")
    parent_key = arguments.get("parent_key")

    result = await jira_client.create_issue(
        project_key=project_key,
        summary=summary,
        description=description,
        issue_type=issue_type,
        priority=priority,
        assignee=assignee,
        labels=labels,
        parent_key=parent_key,
    )

    response = {
        "success": True,
        "issue_key": result.get("key"),
        "issue_id": result.get("id"),
        "self": result.get("self"),
        "details": {
            "project": project_key,
            "type": issue_type,
            "summary": summary,
            "parent": parent_key if parent_key else None,
        },
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_create_subtask(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle create_subtask tool call."""
    parent_key = arguments["parent_key"]
    summary = arguments["summary"]
    description = arguments["description"]
    assignee = arguments.get("assignee")
    priority = arguments.get("priority")

    result = await jira_client.create_subtask(
        parent_key=parent_key,
        summary=summary,
        description=description,
        assignee=assignee,
        priority=priority,
    )

    response = {
        "success": True,
        "subtask_key": result.get("key"),
        "subtask_id": result.get("id"),
        "self": result.get("self"),
        "details": {
            "parent": parent_key,
            "summary": summary,
            "type": "Subtask",
        },
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_get_subtasks(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle get_subtasks tool call."""
    issue_key = arguments["issue_key"]

    subtasks = await jira_client.get_subtasks(issue_key)

    # Format subtasks for response
    formatted_subtasks = []
    for subtask in subtasks:
        fields = subtask.get("fields", {})
        formatted_subtasks.append(
            {
                "key": subtask.get("key"),
                "summary": fields.get("summary"),
                "status": fields.get("status", {}).get("name"),
                "assignee": (
                    fields.get("assignee", {}).get("displayName")
                    if fields.get("assignee")
                    else "Unassigned"
                ),
                "priority": (
                    fields.get("priority", {}).get("name") if fields.get("priority") else None
                ),
                "created": fields.get("created"),
                "updated": fields.get("updated"),
            }
        )

    response = {
        "parent_key": issue_key,
        "subtasks": formatted_subtasks,
        "total": len(formatted_subtasks),
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_assign_issue(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle assign_issue tool call."""
    issue_key = arguments["issue_key"]
    assignee = arguments["assignee"]

    await jira_client.assign_issue(issue_key, assignee)

    response = {
        "success": True,
        "issue_key": issue_key,
        "assignee": assignee if assignee not in ["-1", "null"] else "Unassigned/Automatic",
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


# Additional Tools
LIST_USERS_TOOL = Tool(
    name="list_users",
    description="""List and search for Jira users.

Use this to find users to assign tickets to, or to get user account IDs.
Search by name, email prefix, or partial match. Leave query empty to list all users.""",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (name, email, or username). Leave empty to list all users.",
            },
            "max_results": {
                "type": "number",
                "description": "Maximum number of results (default: 50)",
                "default": 50,
            },
        },
    },
)

LIST_TICKETS_BY_CREATOR_TOOL = Tool(
    name="list_tickets_by_creator",
    description="""List tickets created by a specific user.

Use this to see all tickets a team member has created.""",
    inputSchema={
        "type": "object",
        "properties": {
            "creator": {
                "type": "string",
                "description": "Creator email, username, or 'currentUser()' for yourself",
            },
            "project": {
                "type": "string",
                "description": "Filter by project key (optional, uses default if not specified)",
            },
            "status": {
                "type": "string",
                "description": "Filter by status (optional)",
            },
            "max_results": {
                "type": "number",
                "description": "Maximum number of results (default: 50)",
                "default": 50,
            },
        },
        "required": ["creator"],
    },
)

DELETE_ISSUE_TOOL = Tool(
    name="delete_issue",
    description="""Delete a Jira issue permanently.

⚠️ WARNING: This action cannot be undone! Use with caution.

Use this to remove test tickets, duplicates, or invalid issues.""",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_key": {
                "type": "string",
                "description": "Issue key to delete (e.g., 'SWI-123')",
            },
            "delete_subtasks": {
                "type": "boolean",
                "description": "Whether to delete subtasks as well (default: false)",
                "default": False,
            },
        },
        "required": ["issue_key"],
    },
)

GET_PROJECT_STATUSES_TOOL = Tool(
    name="get_project_statuses",
    description="""Get all available statuses for a project.

Use this to see what statuses are available when updating tickets.
Shows statuses by issue type (Task, Story, Bug, etc.).""",
    inputSchema={
        "type": "object",
        "properties": {
            "project_key": {
                "type": "string",
                "description": "Project key (e.g., 'SWI'). Optional if default project is configured.",
            },
        },
    },
)


async def handle_list_users(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle list_users tool call."""
    query = arguments.get("query", "")
    max_results = arguments.get("max_results", 50)

    # Jira requires a query parameter - use a common letter if none provided
    if not query:
        query = "."  # Search for users with "." in their info (catches most users)

    users = await jira_client.search_users(query=query, max_results=max_results)

    # Format users for response
    formatted_users = []
    for user in users:
        formatted_users.append(
            {
                "accountId": user.get("accountId"),
                "displayName": user.get("displayName"),
                "emailAddress": user.get("emailAddress"),
                "active": user.get("active", True),
            }
        )

    response = {"users": formatted_users, "total": len(formatted_users)}

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_list_tickets_by_creator(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle list_tickets_by_creator tool call."""
    from ..config.settings import Settings
    from ..utils.ticket_parser import parse_ticket_summary

    settings = Settings()

    creator = arguments["creator"]
    status = arguments.get("status")
    max_results = arguments.get("max_results", 50)

    # Use provided project or fall back to default
    project = arguments.get("project")
    if not project and settings.jira_project_key:
        project = settings.jira_project_key

    # Build JQL query
    jql_parts = [f'reporter="{creator}"']

    if project:
        jql_parts.append(f"project={project}")

    if status:
        jql_parts.append(f"status='{status}'")

    jql = " AND ".join(jql_parts)

    # Search issues
    result = await jira_client.search_issues(
        jql=jql,
        max_results=max_results,
        fields=["summary", "status", "priority", "assignee", "created", "updated"],
    )

    # Parse results
    tickets = [parse_ticket_summary(issue) for issue in result.get("issues", [])]

    response = {
        "creator": creator,
        "tickets": tickets,
        "total": result.get("total", 0),
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_delete_issue(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle delete_issue tool call."""
    issue_key = arguments["issue_key"]
    delete_subtasks = arguments.get("delete_subtasks", False)

    await jira_client.delete_issue(issue_key, delete_subtasks=delete_subtasks)

    response = {
        "success": True,
        "deleted_issue": issue_key,
        "deleted_subtasks": delete_subtasks,
        "message": f"Issue {issue_key} has been permanently deleted.",
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_get_project_statuses(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle get_project_statuses tool call."""
    from ..config.settings import Settings

    settings = Settings()

    # Use provided project or fall back to default
    project_key = arguments.get("project_key")
    if not project_key:
        project_key = settings.jira_project_key
        if not project_key:
            raise ValueError(
                "No project_key provided and no default project configured. "
                "Please specify project_key or set JIRA_PROJECT_KEY."
            )

    result = await jira_client.get_project_statuses(project_key)

    return [TextContent(type="text", text=json.dumps(result, indent=2))]
