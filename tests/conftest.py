"""Pytest configuration and fixtures."""

import pytest
import os


def pytest_configure(config):
    """Configure pytest - set environment variables before imports."""
    os.environ["JIRA_URL"] = "https://test.atlassian.net"
    os.environ["JIRA_EMAIL"] = "test@example.com"
    os.environ["JIRA_API_TOKEN"] = "test-token"
    os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture(autouse=True)
def mock_env():
    """Mock environment variables for tests."""
    # Environment variables already set in pytest_configure
    yield


@pytest.fixture
def sample_issue():
    """Sample Jira issue data for testing."""
    return {
        "key": "TEST-123",
        "fields": {
            "summary": "Implement user authentication",
            "description": "# Requirements\n- OAuth2 implementation\n- JWT token generation\n\n# Acceptance Criteria\n- Users can login with email/password\n- JWT tokens expire after 24 hours",
            "status": {"name": "To Do"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "John Doe"},
            "reporter": {"displayName": "Jane Smith"},
            "created": "2025-01-01T00:00:00Z",
            "updated": "2025-01-02T00:00:00Z",
            "labels": ["backend", "security"],
            "components": [{"name": "API"}],
            "comment": {
                "comments": [
                    {
                        "author": {"displayName": "Jane Smith"},
                        "body": "Please use OAuth2",
                        "created": "2025-01-01T10:00:00Z",
                    }
                ]
            },
        },
    }


@pytest.fixture
def mock_http_response_200():
    """Mock successful HTTP response."""

    class MockResponse200:
        status_code = 200
        content = b'{"success": true}'

        def raise_for_status(self):
            pass

        def json(self):
            return {"success": True}

    return MockResponse200


@pytest.fixture
def mock_http_response_429():
    """Mock rate limit HTTP response."""
    import httpx

    class MockResponse429:
        status_code = 429
        text = "Rate limit exceeded"

        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "429 Too Many Requests",
                request=httpx.Request("GET", "https://test.atlassian.net"),
                response=self,
            )

    return MockResponse429
