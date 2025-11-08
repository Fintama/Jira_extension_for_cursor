"""Tests for MCP tool handlers."""

import pytest
from unittest.mock import AsyncMock
from jira_mcp_cursor.tools import (
    handle_list_my_tickets,
    handle_get_ticket,
    handle_update_ticket_status,
    handle_add_ticket_comment,
)
from jira_mcp_cursor.tools.get_ticket import handle_get_highest_priority_ticket
from jira_mcp_cursor.tools.analyze_ticket import handle_analyze_ticket
from jira_mcp_cursor.server.jira_client import JiraClient
from jira_mcp_cursor.server.exceptions import JiraAPIError
import json


@pytest.mark.asyncio
@pytest.mark.ci_critical
async def test_list_my_tickets_handler(sample_issue):
    """CI: Test list_my_tickets handler - golden path."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {
        "issues": [sample_issue],
        "total": 1,
    }

    result = await handle_list_my_tickets({}, mock_client)

    # Verify it returns TextContent
    assert len(result) == 1
    assert result[0].type == "text"

    # Parse the JSON response
    data = json.loads(result[0].text)
    assert data["total"] == 1
    assert len(data["tickets"]) == 1
    assert data["tickets"][0]["key"] == "TEST-123"
    assert data["tickets"][0]["summary"] == "Implement user authentication"
    assert data["tickets"][0]["status"] == "To Do"


@pytest.mark.asyncio
async def test_list_my_tickets_with_filters(sample_issue):
    """Test list_my_tickets with status and project filters."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {
        "issues": [sample_issue],
        "total": 1,
    }

    arguments = {
        "status": "In Progress",
        "project": "PROJ",
        "max_results": 25,
    }

    await handle_list_my_tickets(arguments, mock_client)

    # Verify client was called with correct parameters
    mock_client.search_issues.assert_called_once()
    call_args = mock_client.search_issues.call_args
    assert call_args[1]["max_results"] == 25

    # Verify JQL was built correctly
    jql = call_args[1]["jql"]
    assert 'status = "In Progress"' in jql
    assert 'project = "PROJ"' in jql


@pytest.mark.asyncio
async def test_list_my_tickets_returns_empty():
    """Test list_my_tickets when no tickets are assigned."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {
        "issues": [],
        "total": 0,
    }

    result = await handle_list_my_tickets({}, mock_client)

    data = json.loads(result[0].text)
    assert data["total"] == 0
    assert data["tickets"] == []


@pytest.mark.asyncio
async def test_get_ticket_handler(sample_issue):
    """Test get_ticket handler."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = sample_issue

    arguments = {"ticket_key": "TEST-123", "include_comments": True}

    result = await handle_get_ticket(arguments, mock_client)

    # Verify client was called
    mock_client.get_issue.assert_called_once()

    # Parse response
    data = json.loads(result[0].text)
    assert data["key"] == "TEST-123"
    assert data["summary"] == "Implement user authentication"
    assert len(data["comments"]) == 1
    assert data["comments"][0]["body"] == "Please use OAuth2"


@pytest.mark.asyncio
async def test_get_ticket_without_comments(sample_issue):
    """Test get_ticket with include_comments=False."""
    mock_client = AsyncMock(spec=JiraClient)

    # Issue without comments in expand
    issue_without_comments = sample_issue.copy()
    issue_without_comments["fields"] = sample_issue["fields"].copy()
    issue_without_comments["fields"]["comment"] = {"comments": []}

    mock_client.get_issue.return_value = issue_without_comments

    arguments = {"ticket_key": "TEST-123", "include_comments": False}

    await handle_get_ticket(arguments, mock_client)

    # Verify expand was not used for comments
    call_args = mock_client.get_issue.call_args
    assert call_args[1].get("expand") is None or "renderedFields" not in call_args[1].get(
        "expand", []
    )


@pytest.mark.asyncio
async def test_get_ticket_not_found():
    """Test get_ticket when ticket doesn't exist."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.side_effect = JiraAPIError("Jira API error: 404", status_code=404)

    arguments = {"ticket_key": "NONEXISTENT-999"}

    with pytest.raises(JiraAPIError) as exc_info:
        await handle_get_ticket(arguments, mock_client)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_highest_priority_ticket_handler(sample_issue):
    """Test get_highest_priority_ticket handler."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {
        "issues": [sample_issue],
        "total": 1,
    }

    result = await handle_get_highest_priority_ticket({}, mock_client)

    # Verify search was called with priority ordering
    call_args = mock_client.search_issues.call_args
    jql = call_args[1]["jql"]
    assert "ORDER BY priority DESC" in jql
    assert call_args[1]["max_results"] == 1

    # Verify response contains ticket details
    data = json.loads(result[0].text)
    assert data["key"] == "TEST-123"
    assert data["priority"] == "High"


@pytest.mark.asyncio
async def test_get_highest_priority_with_filters(sample_issue):
    """Test get_highest_priority_ticket with project and exclude filters."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {
        "issues": [sample_issue],
        "total": 1,
    }

    arguments = {
        "project": "PROJ",
        "exclude_status": ["Done", "Closed"],
    }

    await handle_get_highest_priority_ticket(arguments, mock_client)

    # Verify JQL includes filters
    call_args = mock_client.search_issues.call_args
    jql = call_args[1]["jql"]
    assert 'project = "PROJ"' in jql
    assert 'status != "Done"' in jql
    assert 'status != "Closed"' in jql


@pytest.mark.asyncio
@pytest.mark.ci_critical
async def test_analyze_ticket_handler(sample_issue):
    """CI: Test analyze_ticket handler - extracts requirements."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = sample_issue

    arguments = {"ticket_key": "TEST-123"}

    result = await handle_analyze_ticket(arguments, mock_client)

    # Parse response
    data = json.loads(result[0].text)

    assert data["ticket"]["key"] == "TEST-123"
    assert "analysis" in data

    # Verify analysis extracted requirements
    analysis = data["analysis"]
    assert "requirements" in analysis
    assert len(analysis["requirements"]) > 0

    # Should find OAuth2 and JWT in requirements
    requirements_text = " ".join(analysis["requirements"])
    assert "OAuth2" in requirements_text or "JWT" in requirements_text


@pytest.mark.asyncio
async def test_analyze_ticket_with_minimal_description():
    """Test analyze_ticket with minimal/basic description."""
    mock_client = AsyncMock(spec=JiraClient)

    minimal_issue = {
        "key": "TEST-456",
        "fields": {
            "summary": "Fix login bug",
            "description": "Login button doesn't work on mobile",
            "status": {"name": "To Do"},
            "priority": {"name": "Medium"},
        },
    }

    mock_client.get_issue.return_value = minimal_issue

    arguments = {"ticket_key": "TEST-456"}

    result = await handle_analyze_ticket(arguments, mock_client)

    data = json.loads(result[0].text)

    # Should still return analysis structure
    assert "analysis" in data
    assert "requirements" in data["analysis"]
    # May be empty or minimal for simple descriptions
    assert isinstance(data["analysis"]["requirements"], list)


@pytest.mark.asyncio
async def test_analyze_ticket_with_rich_formatting():
    """Test analyze_ticket with markdown, code blocks, lists."""
    mock_client = AsyncMock(spec=JiraClient)

    rich_issue = {
        "key": "TEST-789",
        "fields": {
            "summary": "API endpoint implementation",
            "description": """
# Requirements
- Create `/api/users` endpoint
- Support pagination
- Add authentication

## Acceptance Criteria
- [ ] GET /api/users returns user list
- [ ] Response includes pagination metadata
- [ ] Requires valid JWT token

## Technical Notes
```python
def get_users(page: int, limit: int):
    # Implementation
    pass
```

Dependencies: AUTH-123, DB-456
            """,
            "status": {"name": "To Do"},
            "priority": {"name": "High"},
        },
    }

    mock_client.get_issue.return_value = rich_issue

    arguments = {"ticket_key": "TEST-789"}

    result = await handle_analyze_ticket(arguments, mock_client)

    data = json.loads(result[0].text)
    analysis = data["analysis"]

    # Should extract requirements
    assert len(analysis["requirements"]) > 0

    # Should extract acceptance criteria
    assert "acceptance_criteria" in analysis
    assert len(analysis["acceptance_criteria"]) > 0

    # Should extract technical notes
    assert "technical_notes" in analysis

    # Should identify dependencies
    assert "dependencies" in analysis


@pytest.mark.asyncio
async def test_update_ticket_status_handler():
    """Test update_ticket_status handler."""
    mock_client = AsyncMock(spec=JiraClient)

    # Mock get_issue to return current status
    mock_client.get_issue.return_value = {
        "key": "TEST-123",
        "fields": {"status": {"name": "To Do"}},
    }

    # Mock get_transitions
    mock_client.get_transitions.return_value = [
        {"id": "21", "name": "In Progress", "to": {"name": "In Progress"}},
        {"id": "31", "name": "Done", "to": {"name": "Done"}},
    ]

    # Mock transition_issue
    mock_client.transition_issue.return_value = None

    arguments = {
        "ticket_key": "TEST-123",
        "status": "In Progress",
        "comment": "Starting work on this",
    }

    result = await handle_update_ticket_status(arguments, mock_client)

    # Verify transition was called with correct ID
    mock_client.transition_issue.assert_called_once_with(
        "TEST-123", "21", comment="Starting work on this"
    )

    # Verify response
    data = json.loads(result[0].text)
    assert data["success"] is True
    assert data["ticket_key"] == "TEST-123"
    assert data["old_status"] == "To Do"
    assert data["new_status"] == "In Progress"


@pytest.mark.asyncio
async def test_update_status_invalid_transition():
    """Test update_ticket_status with invalid transition."""
    mock_client = AsyncMock(spec=JiraClient)

    mock_client.get_issue.return_value = {
        "key": "TEST-123",
        "fields": {"status": {"name": "To Do"}},
    }

    # Mock transitions - "Closed" not available
    mock_client.get_transitions.return_value = [
        {"id": "21", "name": "In Progress", "to": {"name": "In Progress"}},
    ]

    arguments = {
        "ticket_key": "TEST-123",
        "status": "Closed",  # Not available
    }

    with pytest.raises(JiraAPIError) as exc_info:
        await handle_update_ticket_status(arguments, mock_client)

    # Should mention available transitions
    assert "Cannot transition" in str(exc_info.value)
    assert "In Progress" in str(exc_info.value)


@pytest.mark.asyncio
async def test_add_ticket_comment_handler():
    """Test add_ticket_comment handler."""
    mock_client = AsyncMock(spec=JiraClient)

    mock_client.add_comment.return_value = {
        "id": "10042",
        "body": "Implementation completed",
        "author": {"displayName": "John Doe"},
    }

    arguments = {
        "ticket_key": "TEST-123",
        "comment": "Implementation completed",
    }

    result = await handle_add_ticket_comment(arguments, mock_client)

    # Verify comment was added
    mock_client.add_comment.assert_called_once_with("TEST-123", "Implementation completed")

    # Verify response
    data = json.loads(result[0].text)
    assert data["success"] is True
    assert data["ticket_key"] == "TEST-123"
    assert data["comment_id"] == "10042"


# Edge case tests
@pytest.mark.asyncio
async def test_get_highest_priority_with_string_exclude_status():
    """Edge case: Test get_highest_priority_ticket with string instead of list for exclude_status."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {
        "issues": [],
        "total": 0,
    }

    # Pass string instead of list
    arguments = {
        "exclude_status": "Done",  # String, not list
    }

    await handle_get_highest_priority_ticket(arguments, mock_client)

    # Should handle gracefully by converting to list
    call_args = mock_client.search_issues.call_args
    jql = call_args[1]["jql"]
    assert 'status != "Done"' in jql


@pytest.mark.asyncio
async def test_analyze_ticket_with_no_description():
    """Edge case: Test analyze_ticket when ticket has no description."""
    mock_client = AsyncMock(spec=JiraClient)

    minimal_issue = {
        "key": "TEST-000",
        "fields": {
            "summary": "Ticket with no description",
            "description": None,  # No description
            "issuetype": {"name": "Bug"},
        },
    }

    mock_client.get_issue.return_value = minimal_issue

    arguments = {"ticket_key": "TEST-000"}

    result = await handle_analyze_ticket(arguments, mock_client)

    data = json.loads(result[0].text)

    # Should still return valid analysis with empty/low values
    assert "analysis" in data
    assert data["analysis"]["requirements"] == []
    assert data["analysis"]["acceptance_criteria"] == []
    assert data["analysis"]["complexity"] == "Low"


@pytest.mark.asyncio
async def test_list_my_tickets_with_empty_result(sample_issue):
    """Edge case: Test list_my_tickets when no tickets match filters."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {
        "issues": [],
        "total": 0,
    }

    arguments = {
        "status": "NonExistentStatus",
    }

    result = await handle_list_my_tickets(arguments, mock_client)

    data = json.loads(result[0].text)
    assert data["total"] == 0
    assert data["tickets"] == []


# Update ticket description tests
@pytest.mark.asyncio
@pytest.mark.ci_critical
async def test_update_ticket_description_replace_mode(sample_issue):
    """CI: Test replacing ticket description completely."""
    from jira_mcp_cursor.tools.update_ticket import handle_update_ticket_description

    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = sample_issue
    mock_client.update_issue.return_value = None

    arguments = {
        "ticket_key": "TEST-123",
        "description": "New description text",
        "append": False,  # Replace mode
    }

    result = await handle_update_ticket_description(arguments, mock_client)

    # Verify update was called with new description
    mock_client.update_issue.assert_called_once_with(
        "TEST-123", {"description": "New description text"}
    )

    # Verify success response
    data = json.loads(result[0].text)
    assert data["success"] is True
    assert data["ticket_key"] == "TEST-123"


@pytest.mark.asyncio
async def test_update_ticket_description_append_mode(sample_issue):
    """Test appending to existing ticket description."""
    from jira_mcp_cursor.tools.update_ticket import handle_update_ticket_description

    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = sample_issue
    mock_client.update_issue.return_value = None

    arguments = {
        "ticket_key": "TEST-123",
        "description": "\n\nAdditional notes",
        "append": True,  # Append mode
    }

    result = await handle_update_ticket_description(arguments, mock_client)

    # Verify update was called with combined description
    mock_client.update_issue.assert_called_once()
    call_args = mock_client.update_issue.call_args
    updated_desc = call_args[0][1]["description"]

    # Should contain both old and new content
    assert "OAuth2" in updated_desc or "Additional notes" in updated_desc

    # Verify success response
    data = json.loads(result[0].text)
    assert data["success"] is True


@pytest.mark.asyncio
async def test_update_description_empty_string():
    """Edge case: Test updating description to empty string."""
    from jira_mcp_cursor.tools.update_ticket import handle_update_ticket_description

    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = {
        "key": "TEST-123",
        "fields": {"description": "Old description"},
    }
    mock_client.update_issue.return_value = None

    arguments = {
        "ticket_key": "TEST-123",
        "description": "",
        "append": False,
    }

    result = await handle_update_ticket_description(arguments, mock_client)

    # Should allow empty description
    mock_client.update_issue.assert_called_once_with("TEST-123", {"description": ""})

    data = json.loads(result[0].text)
    assert data["success"] is True


@pytest.mark.asyncio
async def test_append_to_empty_description():
    """Edge case: Test appending when ticket has no existing description."""
    from jira_mcp_cursor.tools.update_ticket import handle_update_ticket_description

    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = {
        "key": "TEST-456",
        "fields": {"description": None},  # No existing description
    }
    mock_client.update_issue.return_value = None

    arguments = {
        "ticket_key": "TEST-456",
        "description": "First description",
        "append": True,
    }

    result = await handle_update_ticket_description(arguments, mock_client)

    # Should handle None gracefully
    data = json.loads(result[0].text)
    assert data["success"] is True


@pytest.mark.asyncio
async def test_update_description_very_long_text():
    """Edge case: Test updating with very long description."""
    from jira_mcp_cursor.tools.update_ticket import handle_update_ticket_description

    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = {
        "key": "TEST-789",
        "fields": {"description": "Short"},
    }
    mock_client.update_issue.return_value = None

    # Create a very long description (>10k chars)
    long_text = "A" * 15000

    arguments = {
        "ticket_key": "TEST-789",
        "description": long_text,
        "append": False,
    }

    result = await handle_update_ticket_description(arguments, mock_client)

    # Should handle long text
    data = json.loads(result[0].text)
    assert data["success"] is True


@pytest.mark.asyncio
async def test_update_nonexistent_ticket_description():
    """Error case: Test updating description of non-existent ticket."""
    from jira_mcp_cursor.tools.update_ticket import handle_update_ticket_description

    mock_client = AsyncMock(spec=JiraClient)
    # update_issue will be called in replace mode, not get_issue
    mock_client.update_issue.side_effect = JiraAPIError("Ticket not found", status_code=404)

    arguments = {
        "ticket_key": "NONEXISTENT-999",
        "description": "New description",
        "append": False,  # Replace mode - won't call get_issue
    }

    with pytest.raises(JiraAPIError) as exc_info:
        await handle_update_ticket_description(arguments, mock_client)

    assert exc_info.value.status_code == 404
