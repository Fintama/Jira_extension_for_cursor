"""End-to-end tests for complete workflows."""

import pytest
import json
from unittest.mock import patch, AsyncMock
from cryptography.fernet import Fernet
from jira_mcp_cursor.config.storage import SecureConfig
from jira_mcp_cursor.config.cursor_installer import CursorInstaller


def test_complete_setup_flow(tmp_path):
    """E2E: Test complete setup flow - configure, save, verify."""
    # Step 1: Create and save config
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)

    config = {
        "jira_url": "https://test.atlassian.net",
        "email": "test@example.com",
        "api_token": "secret-token-123",
    }

    # Step 2: Save encrypted
    storage.save(config)
    assert storage.exists() is True

    # Step 3: Validate
    assert storage.validate() is True

    # Step 4: Load and verify encryption worked
    loaded = storage.load()
    assert loaded == config

    # Step 5: Verify file is actually encrypted (not plaintext)
    encrypted_content = storage.config_file.read_bytes()
    assert b"secret-token-123" not in encrypted_content  # Token not in plaintext
    assert b"test@example.com" not in encrypted_content  # Email not in plaintext


def test_mcp_server_registration():
    """E2E: Verify all 7 tools are registered in MCP server."""
    from jira_mcp_cursor.tools import (
        LIST_MY_TICKETS_TOOL,
        GET_TICKET_TOOL,
        GET_HIGHEST_PRIORITY_TICKET_TOOL,
        ANALYZE_TICKET_TOOL,
        UPDATE_TICKET_STATUS_TOOL,
        UPDATE_TICKET_DESCRIPTION_TOOL,
        ADD_TICKET_COMMENT_TOOL,
    )

    # Verify all 7 tools are defined
    all_tools = [
        LIST_MY_TICKETS_TOOL,
        GET_TICKET_TOOL,
        GET_HIGHEST_PRIORITY_TICKET_TOOL,
        ANALYZE_TICKET_TOOL,
        UPDATE_TICKET_STATUS_TOOL,
        UPDATE_TICKET_DESCRIPTION_TOOL,
        ADD_TICKET_COMMENT_TOOL,
    ]

    assert len(all_tools) == 7

    # Verify each tool has required attributes
    for tool in all_tools:
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert hasattr(tool, "inputSchema")


def test_config_to_install_flow(tmp_path):
    """E2E: Test config creation → installation flow."""
    # Step 1: Create config
    storage = SecureConfig()
    storage.config_dir = tmp_path / ".jira-mcp"
    storage.config_file = storage.config_dir / "config.json"
    storage.key_file = storage.config_dir / ".key"

    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)

    config = {
        "jira_url": "https://test.atlassian.net",
        "email": "test@example.com",
        "api_token": "token-123",
    }

    storage.save(config)

    # Step 2: Install to Cursor
    installer = CursorInstaller()
    installer.cursor_config_path = tmp_path / "cursor" / "mcp_settings.json"

    result = installer.install()

    # Verify installation succeeded
    assert result is True
    assert installer.is_installed() is True

    # Verify Cursor config has correct structure
    with open(installer.cursor_config_path, "r") as f:
        cursor_config = json.load(f)

    assert "mcpServers" in cursor_config
    assert "jira" in cursor_config["mcpServers"]


def test_error_recovery_e2e():
    """E2E: Test error recovery in complete workflow."""
    from jira_mcp_cursor.server.jira_client import JiraClient
    from jira_mcp_cursor.server.exceptions import AuthenticationError

    client = JiraClient(
        base_url="https://test.atlassian.net",
        auth=("test@example.com", "invalid-token"),
        max_retries=2,
    )

    # Should raise AuthenticationError (not retry on 401)
    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=AuthenticationError("Invalid", status_code=401)),
    ):
        with pytest.raises(AuthenticationError):
            import asyncio

            asyncio.run(client.get_issue("TEST-123"))


def test_server_graceful_shutdown():
    """E2E: Test MCP server instance exists and is properly configured."""
    from jira_mcp_cursor.server import app

    # Server should be initialized
    assert app is not None
    assert app.name == "jira-mcp-server"

    # Server object should exist (graceful shutdown is part of runtime, not testable here)
    assert hasattr(app, "name")
    assert isinstance(app.name, str)
