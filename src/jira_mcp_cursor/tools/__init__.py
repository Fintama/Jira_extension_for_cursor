"""MCP tools for Jira operations."""

from .list_tickets import LIST_MY_TICKETS_TOOL, handle_list_my_tickets
from .get_ticket import (
    GET_TICKET_TOOL,
    GET_HIGHEST_PRIORITY_TICKET_TOOL,
    handle_get_ticket,
    handle_get_highest_priority_ticket,
)
from .update_ticket import (
    UPDATE_TICKET_STATUS_TOOL,
    ADD_TICKET_COMMENT_TOOL,
    UPDATE_TICKET_DESCRIPTION_TOOL,
    handle_update_ticket_status,
    handle_add_ticket_comment,
    handle_update_ticket_description,
)
from .analyze_ticket import ANALYZE_TICKET_TOOL, handle_analyze_ticket

__all__ = [
    "LIST_MY_TICKETS_TOOL",
    "handle_list_my_tickets",
    "GET_TICKET_TOOL",
    "handle_get_ticket",
    "GET_HIGHEST_PRIORITY_TICKET_TOOL",
    "handle_get_highest_priority_ticket",
    "UPDATE_TICKET_STATUS_TOOL",
    "ADD_TICKET_COMMENT_TOOL",
    "UPDATE_TICKET_DESCRIPTION_TOOL",
    "handle_update_ticket_status",
    "handle_add_ticket_comment",
    "handle_update_ticket_description",
    "ANALYZE_TICKET_TOOL",
    "handle_analyze_ticket",
]
