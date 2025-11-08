"""Utilities for parsing Jira ticket data."""

from typing import Any


def parse_ticket_summary(issue: dict[str, Any]) -> dict[str, Any]:
    """Parse issue into summary format."""
    fields = issue.get("fields", {})

    return {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "status": fields.get("status", {}).get("name"),
        "priority": fields.get("priority", {}).get("name"),
        "assignee": (
            fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None
        ),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
    }


def parse_ticket_detail(issue: dict[str, Any]) -> dict[str, Any]:
    """Parse issue into detailed format."""
    fields = issue.get("fields", {})

    # Parse comments
    comments = []
    comment_data = fields.get("comment", {})
    for comment in comment_data.get("comments", []):
        comments.append(
            {
                "author": comment.get("author", {}).get("displayName"),
                "body": comment.get("body"),
                "created": comment.get("created"),
            }
        )

    # Parse labels
    labels = fields.get("labels", [])

    # Parse components
    components = [c.get("name") for c in fields.get("components", [])]

    return {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "description": fields.get("description"),
        "status": fields.get("status", {}).get("name"),
        "priority": fields.get("priority", {}).get("name"),
        "assignee": (
            fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None
        ),
        "reporter": (
            fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None
        ),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
        "labels": labels,
        "components": components,
        "comments": comments,
    }
