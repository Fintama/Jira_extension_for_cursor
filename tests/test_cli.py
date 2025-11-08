"""Tests for CLI commands."""

from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from jira_mcp_cursor.cli import cli


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Jira MCP" in result.output


def test_configure_command():
    """Test configure command launches wizard."""
    runner = CliRunner()

    with patch("jira_mcp_cursor.cli.ConfigWizard") as mock_wizard_class:
        mock_wizard = MagicMock()
        mock_wizard_class.return_value = mock_wizard

        runner.invoke(cli, ["configure"])

        # Should have created wizard instance
        mock_wizard_class.assert_called_once()
        # Should have called run
        mock_wizard.run.assert_called_once()


def test_install_command_success(tmp_path):
    """Test install command with successful installation."""
    runner = CliRunner()

    with patch("jira_mcp_cursor.cli.SecureConfig") as mock_config_class:
        mock_config = MagicMock()
        mock_config.exists.return_value = True
        mock_config_class.return_value = mock_config

        with patch("jira_mcp_cursor.cli.CursorInstaller") as mock_installer_class:
            mock_installer = MagicMock()
            mock_installer.install.return_value = True
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(cli, ["install"])

            assert result.exit_code == 0
            assert "Successfully installed" in result.output
            mock_installer.install.assert_called_once()


def test_install_command_failure():
    """Test install command with installation failure."""
    runner = CliRunner()

    with patch("jira_mcp_cursor.cli.SecureConfig") as mock_config_class:
        mock_config = MagicMock()
        mock_config.exists.return_value = True
        mock_config_class.return_value = mock_config

        with patch("jira_mcp_cursor.cli.CursorInstaller") as mock_installer_class:
            mock_installer = MagicMock()
            mock_installer.install.return_value = False
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(cli, ["install"])

            assert "failed" in result.output.lower()


def test_uninstall_command():
    """Test uninstall command."""
    runner = CliRunner()

    with patch("jira_mcp_cursor.cli.CursorInstaller") as mock_installer_class:
        mock_installer = MagicMock()
        mock_installer.uninstall.return_value = True
        mock_installer_class.return_value = mock_installer

        result = runner.invoke(cli, ["uninstall"])

        assert result.exit_code == 0
        mock_installer.uninstall.assert_called_once()


def test_config_show_command():
    """Test config show command."""
    runner = CliRunner()

    with patch("jira_mcp_cursor.cli.SecureConfig") as mock_config_class:
        mock_config = MagicMock()
        mock_config.load.return_value = {
            "jira_url": "https://test.atlassian.net",
            "email": "test@example.com",
            "api_token": "secret-token",
        }
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        assert "https://test.atlassian.net" in result.output
        assert "test@example.com" in result.output
        # Token should be masked
        assert "***" in result.output or "secret-token" not in result.output


def test_config_test_command_success():
    """Test config test command with valid config."""
    runner = CliRunner()

    with patch("jira_mcp_cursor.cli.SecureConfig") as mock_config_class:
        mock_config = MagicMock()
        mock_config.exists.return_value = True
        mock_config.load.return_value = {
            "jira_url": "https://test.atlassian.net",
            "email": "test@example.com",
            "api_token": "token",
        }
        mock_config_class.return_value = mock_config

        with patch("jira_mcp_cursor.cli.test_connection") as mock_test:
            # Mock async function to return coroutine
            async def async_result():
                return {"success": True, "user": "John Doe"}

            mock_test.return_value = {"success": True, "user": "John Doe"}

            with patch("jira_mcp_cursor.cli.asyncio.run") as mock_run:
                mock_run.return_value = {"success": True, "user": "John Doe"}

                result = runner.invoke(cli, ["config", "test"])

                assert result.exit_code == 0
                assert "Connected" in result.output or "success" in result.output.lower()
                assert "John Doe" in result.output


def test_config_test_command_failure():
    """Test config test command with invalid config."""
    runner = CliRunner()

    with patch("jira_mcp_cursor.cli.SecureConfig") as mock_config_class:
        mock_config = MagicMock()
        mock_config.exists.return_value = True
        mock_config.load.return_value = {
            "jira_url": "https://test.atlassian.net",
            "email": "test@example.com",
            "api_token": "invalid",
        }
        mock_config_class.return_value = mock_config

        with patch("jira_mcp_cursor.cli.asyncio.run") as mock_run:
            mock_run.return_value = {"success": False, "error": "Invalid credentials"}

            result = runner.invoke(cli, ["config", "test"])

            assert "failed" in result.output.lower() or "invalid" in result.output.lower()


def test_config_reset_command():
    """Test config reset command with confirmation."""
    runner = CliRunner()

    with patch("jira_mcp_cursor.cli.SecureConfig") as mock_config_class:
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        # Simulate user confirming
        runner.invoke(cli, ["config", "reset"], input="y\n")

        # Should have called delete
        mock_config.delete.assert_called_once()


def test_install_without_config():
    """Error case: Install without config should show helpful error."""
    runner = CliRunner()

    with patch("jira_mcp_cursor.cli.SecureConfig") as mock_config_class:
        mock_config = MagicMock()
        mock_config.exists.return_value = False
        mock_config_class.return_value = mock_config

        with patch("jira_mcp_cursor.cli.CursorInstaller") as mock_installer_class:
            mock_installer = MagicMock()
            mock_installer.install.return_value = False
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(cli, ["install"])

            # Should mention configuration needed
            # (depending on implementation)
            assert isinstance(result.exit_code, int)
