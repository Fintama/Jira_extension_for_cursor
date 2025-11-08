"""Main MCP server implementation."""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import logging

from ..tools import (
    LIST_MY_TICKETS_TOOL,
    GET_TICKET_TOOL,
    GET_HIGHEST_PRIORITY_TICKET_TOOL,
    ANALYZE_TICKET_TOOL,
    UPDATE_TICKET_STATUS_TOOL,
    ADD_TICKET_COMMENT_TOOL,
    UPDATE_TICKET_DESCRIPTION_TOOL,
    handle_list_my_tickets,
    handle_get_ticket,
    handle_get_highest_priority_ticket,
    handle_analyze_ticket,
    handle_update_ticket_status,
    handle_add_ticket_comment,
    handle_update_ticket_description,
)
from ..config import settings
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
        _jira_client = JiraClient(
            base_url=settings.jira_url,
            auth=settings.get_auth(),
            timeout=settings.jira_timeout,
            max_retries=settings.jira_max_retries,
        )
    return _jira_client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        LIST_MY_TICKETS_TOOL,
        GET_TICKET_TOOL,
        GET_HIGHEST_PRIORITY_TICKET_TOOL,
        ANALYZE_TICKET_TOOL,
        UPDATE_TICKET_STATUS_TOOL,
        UPDATE_TICKET_DESCRIPTION_TOOL,
        ADD_TICKET_COMMENT_TOOL,
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    try:
        client = get_jira_client()

        if name == "list_my_tickets":
            return await handle_list_my_tickets(arguments, client)
        elif name == "get_ticket":
            return await handle_get_ticket(arguments, client)
        elif name == "get_highest_priority_ticket":
            return await handle_get_highest_priority_ticket(arguments, client)
        elif name == "analyze_ticket":
            return await handle_analyze_ticket(arguments, client)
        elif name == "update_ticket_status":
            return await handle_update_ticket_status(arguments, client)
        elif name == "update_ticket_description":
            return await handle_update_ticket_description(arguments, client)
        elif name == "add_ticket_comment":
            return await handle_add_ticket_comment(arguments, client)
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
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting Jira MCP Server")
    logger.info(f"Jira URL: {settings.jira_url}")
    logger.info(f"Auth mode: {'Cloud' if settings.is_cloud else 'Server'}")

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)
