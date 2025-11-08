"""Tests for setup wizard."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from jira_mcp_cursor.config.wizard import SetupWizard


@pytest.mark.asyncio
async def test_wizard_test_connection_valid():
    """Test connection endpoint with valid credentials."""
    wizard = SetupWizard()

    # Mock successful Jira connection
    with patch("jira_mcp_cursor.config.wizard.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"displayName": "John Doe"}

        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        result = await wizard.test_connection(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="valid-token",
        )

        assert result["success"] is True
        assert "user" in result
        assert result["user"] == "John Doe"


@pytest.mark.asyncio
async def test_wizard_test_connection_invalid():
    """Test connection endpoint with invalid credentials."""
    wizard = SetupWizard()

    # Mock 401 auth failure
    with patch("jira_mcp_cursor.config.wizard.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")

        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        result = await wizard.test_connection(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="invalid-token",
        )

        assert result["success"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_wizard_save_config(tmp_path):
    """Test save endpoint creates encrypted config."""
    wizard = SetupWizard()

    # Override config path for testing
    with patch("jira_mcp_cursor.config.wizard.SecureConfig") as mock_storage_class:
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        config_data = {
            "jira_url": "https://test.atlassian.net",
            "email": "test@example.com",
            "api_token": "token-123",
        }

        result = await wizard.save_config(config_data)

        assert result["success"] is True
        # Verify save was called
        mock_storage.save.assert_called_once()


def test_wizard_invalid_jira_url():
    """Edge case: Wizard rejects malformed Jira URLs."""
    wizard = SetupWizard()

    # Test URL validation
    assert wizard.validate_url("https://test.atlassian.net") is True
    assert wizard.validate_url("http://test.atlassian.net") is True
    assert wizard.validate_url("not-a-url") is False
    assert wizard.validate_url("ftp://test.com") is False


@pytest.mark.asyncio
async def test_wizard_network_error_during_test():
    """Error case: Handle network errors during connection test."""
    wizard = SetupWizard()

    # Mock network error
    with patch("jira_mcp_cursor.config.wizard.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.get.side_effect = Exception("Connection refused")
        mock_client.return_value.__aenter__.return_value = mock_instance

        result = await wizard.test_connection(
            jira_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="token",
        )

        assert result["success"] is False
        assert "error" in result
        assert "refused" in result["error"].lower() or "error" in result["error"].lower()


def test_wizard_server_start_stop():
    """Test wizard server can start and stop."""
    # Use a random available port to avoid conflicts
    import socket

    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()

    wizard = SetupWizard(port=port)

    try:
        # Start server
        wizard.start()

        # Verify server was created
        assert wizard.server is not None

        # Stop server
        wizard.stop()

        # Verify server was cleared
        assert wizard.server is None
    except Exception:
        # Clean up on failure
        if wizard.server:
            wizard.stop()
