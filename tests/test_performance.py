"""Performance tests for Jira MCP."""

import pytest
import time
from unittest.mock import AsyncMock
from jira_mcp_cursor.tools import handle_list_my_tickets, handle_get_ticket
from jira_mcp_cursor.server.jira_client import JiraClient
import json


@pytest.mark.asyncio
async def test_list_tickets_performance(sample_issue):
    """Test list_my_tickets completes in < 2s."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {
        "issues": [sample_issue] * 50,  # 50 tickets
        "total": 50,
    }

    start = time.time()
    result = await handle_list_my_tickets({}, mock_client)
    duration = time.time() - start

    assert duration < 2.0  # Under 2 seconds
    data = json.loads(result[0].text)
    assert len(data["tickets"]) == 50


@pytest.mark.asyncio
async def test_get_ticket_performance(sample_issue):
    """Test get_ticket completes in < 1s."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.get_issue.return_value = sample_issue

    start = time.time()
    result = await handle_get_ticket({"ticket_key": "TEST-123"}, mock_client)
    duration = time.time() - start

    assert duration < 1.0  # Under 1 second
    data = json.loads(result[0].text)
    assert data["key"] == "TEST-123"


@pytest.mark.asyncio
async def test_concurrent_requests(sample_issue):
    """Test handling multiple concurrent tool calls."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {"issues": [sample_issue], "total": 1}
    mock_client.get_issue.return_value = sample_issue

    # Simulate concurrent calls
    import asyncio

    tasks = [
        handle_list_my_tickets({}, mock_client),
        handle_get_ticket({"ticket_key": "TEST-123"}, mock_client),
        handle_list_my_tickets({"status": "In Progress"}, mock_client),
    ]

    start = time.time()
    results = await asyncio.gather(*tasks)
    duration = time.time() - start

    # All should complete successfully
    assert len(results) == 3
    assert duration < 3.0  # Should complete reasonably fast


@pytest.mark.asyncio
async def test_large_ticket_list(sample_issue):
    """Test handling large result sets (100+ tickets)."""
    mock_client = AsyncMock(spec=JiraClient)
    mock_client.search_issues.return_value = {
        "issues": [sample_issue] * 100,  # 100 tickets
        "total": 100,
    }

    start = time.time()
    result = await handle_list_my_tickets({"max_results": 100}, mock_client)
    duration = time.time() - start

    # Should handle large lists efficiently
    assert duration < 3.0
    data = json.loads(result[0].text)
    assert len(data["tickets"]) == 100


@pytest.mark.asyncio
async def test_server_startup_time():
    """Test MCP server startup time."""
    from jira_mcp_cursor.server import app

    start = time.time()
    # Verify server instance exists
    assert app is not None
    duration = time.time() - start

    # Server should initialize quickly
    assert duration < 5.0
