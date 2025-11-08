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
from .create_ticket import (
    CREATE_ISSUE_TOOL,
    CREATE_SUBTASK_TOOL,
    GET_SUBTASKS_TOOL,
    ASSIGN_ISSUE_TOOL,
    LIST_USERS_TOOL,
    LIST_TICKETS_BY_CREATOR_TOOL,
    DELETE_ISSUE_TOOL,
    GET_PROJECT_STATUSES_TOOL,
    handle_create_issue,
    handle_create_subtask,
    handle_get_subtasks,
    handle_assign_issue,
    handle_list_users,
    handle_list_tickets_by_creator,
    handle_delete_issue,
    handle_get_project_statuses,
)

__all__ = [
    # Read operations
    "LIST_MY_TICKETS_TOOL",
    "handle_list_my_tickets",
    "GET_TICKET_TOOL",
    "handle_get_ticket",
    "GET_HIGHEST_PRIORITY_TICKET_TOOL",
    "handle_get_highest_priority_ticket",
    "GET_SUBTASKS_TOOL",
    "handle_get_subtasks",
    "LIST_USERS_TOOL",
    "handle_list_users",
    "LIST_TICKETS_BY_CREATOR_TOOL",
    "handle_list_tickets_by_creator",
    "GET_PROJECT_STATUSES_TOOL",
    "handle_get_project_statuses",
    # Analysis
    "ANALYZE_TICKET_TOOL",
    "handle_analyze_ticket",
    # Create operations
    "CREATE_ISSUE_TOOL",
    "handle_create_issue",
    "CREATE_SUBTASK_TOOL",
    "handle_create_subtask",
    # Update operations
    "UPDATE_TICKET_STATUS_TOOL",
    "handle_update_ticket_status",
    "UPDATE_TICKET_DESCRIPTION_TOOL",
    "handle_update_ticket_description",
    "ADD_TICKET_COMMENT_TOOL",
    "handle_add_ticket_comment",
    "ASSIGN_ISSUE_TOOL",
    "handle_assign_issue",
    # Delete operations
    "DELETE_ISSUE_TOOL",
    "handle_delete_issue",
]
