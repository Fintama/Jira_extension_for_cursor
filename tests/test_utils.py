"""Tests for utility functions."""

from jira_mcp_cursor.utils import (
    build_my_tickets_jql,
    build_highest_priority_jql,
    parse_ticket_summary,
    parse_ticket_detail,
)


def test_build_my_tickets_jql_basic():
    """Test basic JQL building."""
    jql = build_my_tickets_jql()
    assert jql == "assignee = currentUser()"


def test_build_my_tickets_jql_with_status():
    """Test JQL building with status filter."""
    jql = build_my_tickets_jql(status="In Progress")
    assert 'status = "In Progress"' in jql
    assert "assignee = currentUser()" in jql


def test_build_my_tickets_jql_with_project():
    """Test JQL building with project filter."""
    jql = build_my_tickets_jql(project="PROJ")
    assert 'project = "PROJ"' in jql


def test_build_highest_priority_jql():
    """Test highest priority JQL building."""
    jql = build_highest_priority_jql()
    assert jql.endswith("ORDER BY priority DESC")


def test_parse_ticket_summary():
    """Test parsing ticket summary."""
    issue = {
        "key": "TEST-123",
        "fields": {
            "summary": "Test ticket",
            "status": {"name": "To Do"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "John Doe"},
            "created": "2025-01-01T00:00:00Z",
            "updated": "2025-01-02T00:00:00Z",
        },
    }

    result = parse_ticket_summary(issue)

    assert result["key"] == "TEST-123"
    assert result["summary"] == "Test ticket"
    assert result["status"] == "To Do"
    assert result["priority"] == "High"
    assert result["assignee"] == "John Doe"


def test_parse_ticket_detail():
    """Test parsing ticket detail."""
    issue = {
        "key": "TEST-123",
        "fields": {
            "summary": "Test ticket",
            "description": "Test description",
            "status": {"name": "To Do"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "John Doe"},
            "reporter": {"displayName": "Jane Smith"},
            "created": "2025-01-01T00:00:00Z",
            "updated": "2025-01-02T00:00:00Z",
            "labels": ["backend", "urgent"],
            "components": [{"name": "API"}],
            "comment": {
                "comments": [
                    {
                        "author": {"displayName": "John Doe"},
                        "body": "Test comment",
                        "created": "2025-01-01T10:00:00Z",
                    }
                ]
            },
        },
    }

    result = parse_ticket_detail(issue)

    assert result["key"] == "TEST-123"
    assert result["summary"] == "Test ticket"
    assert result["description"] == "Test description"
    assert len(result["labels"]) == 2
    assert len(result["components"]) == 1
    assert len(result["comments"]) == 1
    assert result["comments"][0]["body"] == "Test comment"


def test_build_my_tickets_jql_with_multiple_exclude_statuses():
    """Test JQL building with multiple exclude statuses."""
    jql = build_my_tickets_jql(exclude_statuses=["Done", "Closed", "Cancelled"])

    assert "assignee = currentUser()" in jql
    assert 'status != "Done"' in jql
    assert 'status != "Closed"' in jql
    assert 'status != "Cancelled"' in jql


def test_build_my_tickets_jql_with_all_filters():
    """Test JQL building with all filters combined."""
    jql = build_my_tickets_jql(status="In Progress", project="PROJ", exclude_statuses=["Done"])

    assert "assignee = currentUser()" in jql
    assert 'status = "In Progress"' in jql
    assert 'project = "PROJ"' in jql
    assert 'status != "Done"' in jql
    assert jql.count("AND") == 3  # Should have 3 AND operators


def test_build_highest_priority_jql_with_project():
    """Test highest priority JQL with project filter."""
    jql = build_highest_priority_jql(project="PROJ", exclude_statuses=["Done", "Closed"])

    assert "assignee = currentUser()" in jql
    assert 'project = "PROJ"' in jql
    assert 'status != "Done"' in jql
    assert 'status != "Closed"' in jql
    assert jql.endswith("ORDER BY priority DESC")


def test_parse_ticket_with_no_assignee():
    """Test parsing ticket with no assignee."""
    issue = {
        "key": "TEST-123",
        "fields": {
            "summary": "Unassigned ticket",
            "status": {"name": "To Do"},
            "priority": {"name": "Medium"},
            "assignee": None,  # No assignee
            "created": "2025-01-01T00:00:00Z",
            "updated": "2025-01-02T00:00:00Z",
        },
    }

    result = parse_ticket_summary(issue)

    assert result["key"] == "TEST-123"
    assert result["assignee"] is None


def test_parse_ticket_with_no_comments():
    """Test parsing ticket detail with no comments."""
    issue = {
        "key": "TEST-456",
        "fields": {
            "summary": "Test ticket",
            "description": "Test description",
            "status": {"name": "To Do"},
            "priority": {"name": "Low"},
            "assignee": {"displayName": "John Doe"},
            "reporter": {"displayName": "Jane Smith"},
            "created": "2025-01-01T00:00:00Z",
            "updated": "2025-01-02T00:00:00Z",
            "labels": [],
            "components": [],
            "comment": {"comments": []},  # Empty comments
        },
    }

    result = parse_ticket_detail(issue)

    assert result["key"] == "TEST-456"
    assert result["comments"] == []
    assert result["labels"] == []
    assert result["components"] == []


def test_parse_ticket_with_empty_description():
    """Test parsing ticket with empty/missing description."""
    issue = {
        "key": "TEST-789",
        "fields": {
            "summary": "Ticket without description",
            "description": None,  # No description
            "status": {"name": "To Do"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "John Doe"},
            "reporter": {"displayName": "Jane Smith"},
            "created": "2025-01-01T00:00:00Z",
            "updated": "2025-01-02T00:00:00Z",
            "labels": [],
            "components": [],
            "comment": {"comments": []},
        },
    }

    result = parse_ticket_detail(issue)

    assert result["key"] == "TEST-789"
    assert result["description"] is None
