"""Update ticket tools."""

from typing import Any
from mcp.types import Tool, TextContent
from ..server.jira_client import JiraClient
from ..server.exceptions import JiraAPIError
import json


async def handle_update_ticket_status(
    arguments: dict,
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle update_ticket_status tool call."""
    ticket_key = arguments["ticket_key"]
    target_status = arguments["status"]

    # Get current issue to find old status
    issue = await jira_client.get_issue(ticket_key, fields=["status"])
    old_status = issue["fields"]["status"]["name"]

    # Get available transitions
    transitions = await jira_client.get_transitions(ticket_key)

    # Find transition ID for target status
    transition_id = None
    for transition in transitions:
        if transition["to"]["name"].lower() == target_status.lower():
            transition_id = transition["id"]
            break

    if not transition_id:
        available = [t["to"]["name"] for t in transitions]
        raise JiraAPIError(
            f"Cannot transition to '{target_status}'. Available: {', '.join(available)}"
        )

    # Perform transition
    await jira_client.transition_issue(
        ticket_key,
        transition_id,
        comment=arguments.get("comment"),
    )

    response = {
        "success": True,
        "ticket_key": ticket_key,
        "old_status": old_status,
        "new_status": target_status,
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_add_ticket_comment(
    arguments: dict,
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle add_ticket_comment tool call."""
    result = await jira_client.add_comment(
        arguments["ticket_key"],
        arguments["comment"],
    )

    response = {
        "success": True,
        "ticket_key": arguments["ticket_key"],
        "comment_id": result.get("id"),
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def handle_update_ticket_description(
    arguments: dict[str, Any],
    jira_client: JiraClient,
) -> list[TextContent]:
    """Handle update_ticket_description tool call.

    Updates a ticket's description either by replacing it entirely or appending to it.
    In append mode, fetches the existing description first, then combines it with new text.

    Args:
        arguments: Tool arguments including:
            - ticket_key (str): Jira ticket key (e.g., 'PROJ-123')
            - description (str): New description text
            - append (bool): If True, append to existing; if False, replace (default: False)
        jira_client: Jira API client instance

    Returns:
        List of TextContent with success response containing ticket_key

    Raises:
        JiraAPIError: If ticket update fails
        TicketNotFoundError: If ticket doesn't exist
    """
    ticket_key = arguments["ticket_key"]
    new_description = arguments["description"]
    append_mode = arguments.get("append", False)

    # Jira has a practical limit of ~32k chars for descriptions
    # Log a warning if description is very long
    import logging

    logger = logging.getLogger(__name__)

    if len(new_description) > 30000:
        logger.warning(
            f"Description is very long ({len(new_description)} chars). Jira may truncate or reject it."
        )

    # If append mode, fetch existing description first
    if append_mode:
        issue = await jira_client.get_issue(ticket_key, fields=["description"])
        existing_description = issue.get("fields", {}).get("description") or ""

        # Combine existing and new description
        if existing_description:
            combined_description = existing_description + new_description
        else:
            combined_description = new_description

        final_description = combined_description
    else:
        # Replace mode - use new description as-is
        final_description = new_description

    # Update the ticket
    await jira_client.update_issue(ticket_key, {"description": final_description})

    response = {
        "success": True,
        "ticket_key": ticket_key,
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


# Tool definitions
UPDATE_TICKET_STATUS_TOOL = Tool(
    name="update_ticket_status",
    description="Transition ticket to a new status",
    inputSchema={
        "type": "object",
        "properties": {
            "ticket_key": {
                "type": "string",
                "description": "Jira ticket key",
            },
            "status": {
                "type": "string",
                "description": "Target status name",
            },
            "comment": {
                "type": "string",
                "description": "Optional comment to add",
            },
        },
        "required": ["ticket_key", "status"],
    },
)

ADD_TICKET_COMMENT_TOOL = Tool(
    name="add_ticket_comment",
    description="Add a comment to a ticket",
    inputSchema={
        "type": "object",
        "properties": {
            "ticket_key": {
                "type": "string",
                "description": "Jira ticket key",
            },
            "comment": {
                "type": "string",
                "description": "Comment text",
            },
        },
        "required": ["ticket_key", "comment"],
    },
)

UPDATE_TICKET_DESCRIPTION_TOOL = Tool(
    name="update_ticket_description",
    description="Update ticket description",
    inputSchema={
        "type": "object",
        "properties": {
            "ticket_key": {
                "type": "string",
                "description": "Jira ticket key",
            },
            "description": {
                "type": "string",
                "description": "New description text",
            },
            "append": {
                "type": "boolean",
                "description": "Append to existing description instead of replacing",
                "default": False,
            },
        },
        "required": ["ticket_key", "description"],
    },
)
