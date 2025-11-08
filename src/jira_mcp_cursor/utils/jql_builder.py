"""JQL query builder utilities."""

from typing import Optional


def build_my_tickets_jql(
    status: Optional[str] = None,
    project: Optional[str] = None,
    exclude_statuses: Optional[list[str]] = None,
) -> str:
    """Build JQL query for user's assigned tickets."""
    parts = ["assignee = currentUser()"]

    if status:
        parts.append(f'status = "{status}"')

    if project:
        parts.append(f'project = "{project}"')

    if exclude_statuses:
        for status_item in exclude_statuses:
            parts.append(f'status != "{status_item}"')

    return " AND ".join(parts)


def build_highest_priority_jql(
    project: Optional[str] = None,
    exclude_statuses: Optional[list[str]] = None,
) -> str:
    """Build JQL query for highest priority ticket."""
    jql = build_my_tickets_jql(project=project, exclude_statuses=exclude_statuses)
    return f"{jql} ORDER BY priority DESC"
