"""Main MCP server implementation."""

from mcp.server import Server, InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ServerCapabilities, ToolsCapability
import logging

from ..tools import (
    LIST_MY_TICKETS_TOOL,
    GET_TICKET_TOOL,
    GET_HIGHEST_PRIORITY_TICKET_TOOL,
    ANALYZE_TICKET_TOOL,
    UPDATE_TICKET_STATUS_TOOL,
    ADD_TICKET_COMMENT_TOOL,
    UPDATE_TICKET_DESCRIPTION_TOOL,
    CREATE_ISSUE_TOOL,
    CREATE_SUBTASK_TOOL,
    GET_SUBTASKS_TOOL,
    ASSIGN_ISSUE_TOOL,
    LIST_USERS_TOOL,
    LIST_TICKETS_BY_CREATOR_TOOL,
    DELETE_ISSUE_TOOL,
    GET_PROJECT_STATUSES_TOOL,
    handle_list_my_tickets,
    handle_get_ticket,
    handle_get_highest_priority_ticket,
    handle_analyze_ticket,
    handle_update_ticket_status,
    handle_add_ticket_comment,
    handle_update_ticket_description,
    handle_create_issue,
    handle_create_subtask,
    handle_get_subtasks,
    handle_assign_issue,
    handle_list_users,
    handle_list_tickets_by_creator,
    handle_delete_issue,
    handle_get_project_statuses,
)
from .jira_client import JiraClient

logger = logging.getLogger(__name__)

# Create server instance
app = Server("jira-mcp-server")

# Global Jira client (will be initialized in run())
_jira_client: JiraClient | None = None


def get_jira_client() -> JiraClient:
    """Get or create Jira client instance."""
    global _jira_client
    if _jira_client is None:
        # Reload settings to pick up env vars set in CLI
        from ..config.settings import Settings

        current_settings = Settings()

        _jira_client = JiraClient(
            base_url=current_settings.jira_url,
            auth=current_settings.get_auth(),
            timeout=current_settings.jira_timeout,
            max_retries=current_settings.jira_max_retries,
        )
    return _jira_client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        # Read operations
        LIST_MY_TICKETS_TOOL,
        LIST_TICKETS_BY_CREATOR_TOOL,
        GET_TICKET_TOOL,
        GET_HIGHEST_PRIORITY_TICKET_TOOL,
        GET_SUBTASKS_TOOL,
        LIST_USERS_TOOL,
        GET_PROJECT_STATUSES_TOOL,
        # Analysis
        ANALYZE_TICKET_TOOL,
        # Create operations
        CREATE_ISSUE_TOOL,
        CREATE_SUBTASK_TOOL,
        # Update operations
        UPDATE_TICKET_STATUS_TOOL,
        UPDATE_TICKET_DESCRIPTION_TOOL,
        ADD_TICKET_COMMENT_TOOL,
        ASSIGN_ISSUE_TOOL,
        # Delete operations
        DELETE_ISSUE_TOOL,
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    try:
        client = get_jira_client()

        # Read operations
        if name == "list_my_tickets":
            return await handle_list_my_tickets(arguments, client)
        elif name == "list_tickets_by_creator":
            return await handle_list_tickets_by_creator(arguments, client)
        elif name == "get_ticket":
            return await handle_get_ticket(arguments, client)
        elif name == "get_highest_priority_ticket":
            return await handle_get_highest_priority_ticket(arguments, client)
        elif name == "get_subtasks":
            return await handle_get_subtasks(arguments, client)
        elif name == "list_users":
            return await handle_list_users(arguments, client)
        elif name == "get_project_statuses":
            return await handle_get_project_statuses(arguments, client)
        # Analysis
        elif name == "analyze_ticket":
            return await handle_analyze_ticket(arguments, client)
        # Create operations
        elif name == "create_issue":
            return await handle_create_issue(arguments, client)
        elif name == "create_subtask":
            return await handle_create_subtask(arguments, client)
        # Update operations
        elif name == "update_ticket_status":
            return await handle_update_ticket_status(arguments, client)
        elif name == "update_ticket_description":
            return await handle_update_ticket_description(arguments, client)
        elif name == "add_ticket_comment":
            return await handle_add_ticket_comment(arguments, client)
        elif name == "assign_issue":
            return await handle_assign_issue(arguments, client)
        # Delete operations
        elif name == "delete_issue":
            return await handle_delete_issue(arguments, client)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        error_response = {
            "success": False,
            "error": {
                "message": str(e),
                "tool": name,
            },
        }
        import json

        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def run() -> None:
    """Run the MCP server."""
    # Reload settings to pick up env vars
    from ..config.settings import Settings

    current_settings = Settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, current_settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting Jira MCP Server")
    logger.info(f"Jira URL: {current_settings.jira_url}")
    logger.info(f"Auth mode: {'Cloud' if current_settings.is_cloud else 'Server'}")

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="jira-mcp-server",
            server_version="0.1.0",
            capabilities=ServerCapabilities(
                tools=ToolsCapability(listChanged=True),
            ),
        )
        await app.run(read_stream, write_stream, init_options)
