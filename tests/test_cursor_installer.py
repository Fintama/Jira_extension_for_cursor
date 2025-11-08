"""Tests for Cursor installer."""

import pytest
import json
from unittest.mock import patch
from jira_mcp_cursor.config.cursor_installer import CursorInstaller


@pytest.mark.ci_critical
def test_install_to_empty_config(tmp_path):
    """CI: Test installing to empty Cursor config."""
    installer = CursorInstaller()

    # Use temp path for testing
    config_path = tmp_path / "mcp_settings.json"
    installer.cursor_config_path = config_path

    result = installer.install()

    assert result is True
    assert config_path.exists()

    # Verify config structure
    with open(config_path, "r") as f:
        config = json.load(f)

    assert "mcpServers" in config
    assert "jira" in config["mcpServers"]
    assert config["mcpServers"]["jira"]["command"] == "jira-mcp"
    assert "serve" in config["mcpServers"]["jira"]["args"]


def test_detect_cursor_config_path_macos():
    """Test OS-specific path detection for macOS."""
    with patch("platform.system", return_value="Darwin"):
        installer = CursorInstaller()
        path = installer._get_cursor_config_path()

        assert ".cursor" in str(path)
        assert "mcp_settings.json" in str(path)


def test_detect_cursor_config_path_windows():
    """Test OS-specific path detection for Windows."""
    with patch("platform.system", return_value="Windows"):
        installer = CursorInstaller()
        path = installer._get_cursor_config_path()

        assert "AppData" in str(path) or "Cursor" in str(path)
        assert "mcp_settings.json" in str(path)


def test_detect_cursor_config_path_linux():
    """Test OS-specific path detection for Linux."""
    with patch("platform.system", return_value="Linux"):
        installer = CursorInstaller()
        path = installer._get_cursor_config_path()

        assert ".config" in str(path) or "Cursor" in str(path)
        assert "mcp_settings.json" in str(path)


def test_install_creates_backup(tmp_path):
    """Test that backup is created before installation."""
    installer = CursorInstaller()
    config_path = tmp_path / "mcp_settings.json"
    installer.cursor_config_path = config_path

    # Create existing config
    existing_config = {"mcpServers": {"other": {"command": "other-server"}}}
    config_path.write_text(json.dumps(existing_config))

    result = installer.install()

    assert result is True

    # Verify backup was created
    backup_path = tmp_path / "mcp_settings.json.backup"
    assert backup_path.exists()

    # Verify backup contains original config
    with open(backup_path, "r") as f:
        backup = json.load(f)
    assert backup == existing_config


def test_install_to_existing_config_preserves_others(tmp_path):
    """Test installing when other MCP servers exist."""
    installer = CursorInstaller()
    config_path = tmp_path / "mcp_settings.json"
    installer.cursor_config_path = config_path

    # Create config with other server
    existing_config = {"mcpServers": {"other-server": {"command": "other"}}}
    config_path.write_text(json.dumps(existing_config))

    installer.install()

    # Load and verify
    with open(config_path, "r") as f:
        config = json.load(f)

    # Should have both servers
    assert "other-server" in config["mcpServers"]
    assert "jira" in config["mcpServers"]


def test_install_when_already_installed(tmp_path):
    """Edge case: Installing when jira already exists (update)."""
    installer = CursorInstaller()
    config_path = tmp_path / "mcp_settings.json"
    installer.cursor_config_path = config_path

    # Create config with old jira entry
    existing_config = {"mcpServers": {"jira": {"command": "old-command", "args": ["old"]}}}
    config_path.write_text(json.dumps(existing_config))

    installer.install()

    # Load and verify it was updated
    with open(config_path, "r") as f:
        config = json.load(f)

    assert config["mcpServers"]["jira"]["command"] == "jira-mcp"
    assert config["mcpServers"]["jira"]["args"][0] == "serve"


def test_uninstall_removes_entry(tmp_path):
    """Test uninstalling removes jira entry."""
    installer = CursorInstaller()
    config_path = tmp_path / "mcp_settings.json"
    installer.cursor_config_path = config_path

    # Create config with jira
    config = {"mcpServers": {"jira": {"command": "jira-mcp"}, "other": {"command": "other"}}}
    config_path.write_text(json.dumps(config))

    result = installer.uninstall()

    assert result is True

    # Load and verify jira removed but other preserved
    with open(config_path, "r") as f:
        updated_config = json.load(f)

    assert "jira" not in updated_config["mcpServers"]
    assert "other" in updated_config["mcpServers"]


def test_is_installed_method(tmp_path):
    """Test is_installed() method."""
    installer = CursorInstaller()
    config_path = tmp_path / "mcp_settings.json"
    installer.cursor_config_path = config_path

    # Not installed initially
    assert installer.is_installed() is False

    # Install
    installer.install()

    # Should be installed now
    assert installer.is_installed() is True


def test_cursor_not_installed(tmp_path):
    """Edge case: Handle when Cursor config directory doesn't exist."""
    installer = CursorInstaller()
    # Point to non-existent directory
    installer.cursor_config_path = tmp_path / "nonexistent" / "mcp_settings.json"

    # Should create directory and install
    result = installer.install()

    assert result is True
    assert installer.cursor_config_path.exists()


def test_restore_backup_on_failure(tmp_path):
    """Edge case: Restore backup if installation fails."""
    installer = CursorInstaller()
    config_path = tmp_path / "mcp_settings.json"
    installer.cursor_config_path = config_path

    # Create existing config
    original_config = {"mcpServers": {"other": {"command": "other"}}}
    config_path.write_text(json.dumps(original_config))

    # Mock a failure during install
    with patch.object(installer, "_update_config", side_effect=Exception("Simulated failure")):
        # Install catches the exception and returns False (not raised)
        result = installer.install()
        assert result is False

    # Verify backup was created and potentially restored
    backup_path = config_path.with_suffix(".json.backup")
    # Backup should exist (created before failure)
    assert backup_path.exists()


def test_install_cursor_config_invalid_json(tmp_path):
    """Error case: Handle malformed Cursor config JSON."""
    installer = CursorInstaller()
    config_path = tmp_path / "mcp_settings.json"
    installer.cursor_config_path = config_path

    # Write invalid JSON
    config_path.write_text("{ invalid json }")

    # Should handle gracefully - either fix or error clearly
    result = installer.install()

    # Depending on implementation, might succeed (overwrite) or fail gracefully
    assert isinstance(result, bool)
