"""Tests for Jira client."""

import pytest
from unittest.mock import AsyncMock, patch
from jira_mcp_cursor.server.jira_client import JiraClient
from jira_mcp_cursor.server.exceptions import JiraAPIError


@pytest.mark.asyncio
async def test_search_issues():
    """Test searching for issues."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    mock_response = {
        "issues": [
            {
                "key": "TEST-123",
                "fields": {
                    "summary": "Test ticket",
                    "status": {"name": "To Do"},
                    "assignee": {"displayName": "John Doe"},
                },
            },
            {
                "key": "TEST-456",
                "fields": {
                    "summary": "Another ticket",
                    "status": {"name": "In Progress"},
                    "assignee": {"displayName": "John Doe"},
                },
            },
        ],
    }

    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)) as mock_req:
        result = await client.search_issues(
            'assignee = "John Doe"',
            fields=["summary", "status"],
            max_results=10,
        )

        mock_req.assert_called_once_with(
            "POST",
            "/search/jql",
            json={"jql": 'assignee = "John Doe"', "maxResults": 10, "fields": ["summary", "status"]},
            api_version=3,
        )

        assert len(result["issues"]) == 2
        assert result["issues"][0]["key"] == "TEST-123"
        assert result["total"] == 2


@pytest.mark.asyncio
async def test_get_issue():
    """Test getting single issue."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    mock_response = {
        "key": "TEST-123",
        "fields": {
            "summary": "Test ticket",
            "description": "Test description",
        },
    }

    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.get_issue("TEST-123")

        assert result["key"] == "TEST-123"
        assert result["fields"]["summary"] == "Test ticket"


@pytest.mark.asyncio
async def test_update_issue():
    """Test updating issue fields."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    with patch.object(client, "_request", new=AsyncMock(return_value={})):
        await client.update_issue("TEST-123", {"description": "Updated description"})

        # Verify _request was called with correct parameters
        client._request.assert_called_once()
        call_args = client._request.call_args
        assert call_args[0][0] == "PUT"
        assert call_args[0][1] == "/issue/TEST-123"
        assert call_args[1]["json"] == {"fields": {"description": "Updated description"}}


@pytest.mark.asyncio
async def test_get_transitions():
    """Test getting available transitions for an issue."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    mock_response = {
        "transitions": [
            {"id": "11", "name": "To Do", "to": {"name": "To Do"}},
            {"id": "21", "name": "In Progress", "to": {"name": "In Progress"}},
            {"id": "31", "name": "Done", "to": {"name": "Done"}},
        ]
    }

    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.get_transitions("TEST-123")

        assert len(result) == 3
        assert result[0]["id"] == "11"
        assert result[1]["to"]["name"] == "In Progress"


@pytest.mark.asyncio
async def test_transition_issue():
    """Test transitioning issue to new status."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    with patch.object(client, "_request", new=AsyncMock(return_value={})):
        await client.transition_issue("TEST-123", "21", comment="Moving to In Progress")

        # Verify _request was called with correct parameters
        client._request.assert_called_once()
        call_args = client._request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/issue/TEST-123/transitions"

        payload = call_args[1]["json"]
        assert payload["transition"]["id"] == "21"
        assert payload["update"]["comment"][0]["add"]["body"] == "Moving to In Progress"


@pytest.mark.asyncio
async def test_transition_issue_without_comment():
    """Test transitioning issue without adding a comment."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    with patch.object(client, "_request", new=AsyncMock(return_value={})):
        await client.transition_issue("TEST-123", "21")

        # Verify no comment in payload
        call_args = client._request.call_args
        payload = call_args[1]["json"]
        assert "update" not in payload


@pytest.mark.asyncio
async def test_add_comment():
    """Test adding comment to an issue."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    mock_response = {
        "id": "10042",
        "body": "This is a test comment",
        "author": {"displayName": "John Doe"},
    }

    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.add_comment("TEST-123", "This is a test comment")

        assert result["id"] == "10042"
        assert result["body"] == "This is a test comment"

        # Verify _request was called correctly
        client._request.assert_called_once()
        call_args = client._request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/issue/TEST-123/comment"
        assert call_args[1]["json"]["body"] == "This is a test comment"


@pytest.mark.asyncio
async def test_jira_client_http_error():
    """Test Jira client handles HTTP errors correctly."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    # Mock HTTP error response
    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=JiraAPIError("Jira API error: 404", status_code=404)),
    ):
        with pytest.raises(JiraAPIError) as exc_info:
            await client.get_issue("NONEXISTENT-123")

        assert exc_info.value.status_code == 404
        assert "404" in str(exc_info.value)


@pytest.mark.asyncio
async def test_jira_client_network_error():
    """Test Jira client handles network errors correctly."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
    )

    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=JiraAPIError("Request failed: Connection refused")),
    ):
        with pytest.raises(JiraAPIError) as exc_info:
            await client.search_issues("assignee = currentUser()")

        assert "Request failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_jira_client_timeout():
    """Test Jira client handles timeout errors correctly."""
    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "token"),
        timeout=1,  # Very short timeout
    )

    with patch.object(
        client, "_request", new=AsyncMock(side_effect=JiraAPIError("Request failed: Timeout"))
    ):
        with pytest.raises(JiraAPIError) as exc_info:
            await client.get_issue("TEST-123")

        assert "Timeout" in str(exc_info.value) or "Request failed" in str(exc_info.value)
