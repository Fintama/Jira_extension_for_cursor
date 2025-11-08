"""Integration tests for complete workflows."""

import pytest
from unittest.mock import AsyncMock
from jira_mcp_cursor.tools import (
    handle_list_my_tickets,
    handle_get_ticket,
    handle_update_ticket_status,
)
from jira_mcp_cursor.tools.analyze_ticket import handle_analyze_ticket
from jira_mcp_cursor.tools.update_ticket import handle_update_ticket_description
from jira_mcp_cursor.server.jira_client import JiraClient
import json


@pytest.mark.asyncio
async def test_complete_ticket_workflow(sample_issue):
    """Integration: Test complete workflow - list, get, analyze, update."""
    mock_client = AsyncMock(spec=JiraClient)

    # Step 1: List tickets
    mock_client.search_issues.return_value = {
        "issues": [sample_issue],
        "total": 1,
    }

    list_result = await handle_list_my_tickets({}, mock_client)
    list_data = json.loads(list_result[0].text)
    assert list_data["total"] == 1
    ticket_key = list_data["tickets"][0]["key"]

    # Step 2: Get ticket details
    mock_client.get_issue.return_value = sample_issue

    get_result = await handle_get_ticket({"ticket_key": ticket_key}, mock_client)
    get_data = json.loads(get_result[0].text)
    assert get_data["key"] == ticket_key

    # Step 3: Analyze ticket
    analyze_result = await handle_analyze_ticket({"ticket_key": ticket_key}, mock_client)
    analyze_data = json.loads(analyze_result[0].text)
    assert "analysis" in analyze_data
    assert "requirements" in analyze_data["analysis"]

    # Step 4: Update ticket status
    mock_client.get_transitions.return_value = [
        {"id": "21", "name": "In Progress", "to": {"name": "In Progress"}},
    ]
    mock_client.transition_issue.return_value = None

    update_result = await handle_update_ticket_status(
        {"ticket_key": ticket_key, "status": "In Progress"}, mock_client
    )
    update_data = json.loads(update_result[0].text)
    assert update_data["success"] is True

    # Verify all steps executed
    assert mock_client.search_issues.call_count == 1
    assert mock_client.get_issue.call_count >= 2  # Get + Analyze
    assert mock_client.get_transitions.call_count == 1
    assert mock_client.transition_issue.call_count == 1


@pytest.mark.asyncio
async def test_error_recovery_workflow():
    """Integration: Test workflow with error recovery."""
    mock_client = AsyncMock(spec=JiraClient)

    # First call fails, second succeeds
    call_count = {"count": 0}

    async def search_with_retry(*args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] == 1:
            raise Exception("Temporary network error")
        return {"issues": [], "total": 0}

    mock_client.search_issues = search_with_retry

    # Should handle error and retry could succeed
    # (In actual implementation with retry logic)
    with pytest.raises(Exception):
        await handle_list_my_tickets({}, mock_client)

    # Second attempt succeeds
    result = await handle_list_my_tickets({}, mock_client)
    data = json.loads(result[0].text)
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_update_description_workflow(sample_issue):
    """Integration: Test updating ticket description in workflow."""
    mock_client = AsyncMock(spec=JiraClient)

    # Get ticket
    mock_client.get_issue.return_value = sample_issue

    # Update description (replace mode)
    mock_client.update_issue.return_value = None

    result = await handle_update_ticket_description(
        {
            "ticket_key": "TEST-123",
            "description": "Updated description",
            "append": False,
        },
        mock_client,
    )

    data = json.loads(result[0].text)
    assert data["success"] is True

    # Verify update was called
    mock_client.update_issue.assert_called_once()


@pytest.mark.asyncio
async def test_multiple_updates_workflow(sample_issue):
    """Integration: Test multiple updates in sequence."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = sample_issue
    mock_client.update_issue.return_value = None
    mock_client.add_comment.return_value = {"id": "10001"}

    # Update description
    from jira_mcp_cursor.tools import handle_add_ticket_comment

    desc_result = await handle_update_ticket_description(
        {"ticket_key": "TEST-123", "description": "New desc", "append": False},
        mock_client,
    )
    desc_data = json.loads(desc_result[0].text)
    assert desc_data["success"] is True

    # Add comment
    comment_result = await handle_add_ticket_comment(
        {"ticket_key": "TEST-123", "comment": "Description updated"}, mock_client
    )
    comment_data = json.loads(comment_result[0].text)
    assert comment_data["success"] is True

    # Verify both operations executed
    assert mock_client.update_issue.call_count == 1
    assert mock_client.add_comment.call_count == 1
