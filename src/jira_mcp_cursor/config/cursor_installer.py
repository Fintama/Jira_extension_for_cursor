"""Cursor integration and auto-installer."""

import json
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CursorInstaller:
    """Auto-installer for Cursor IDE integration.

    Detects Cursor configuration location, updates MCP settings,
    and manages backups for safe rollback.
    """

    def __init__(self):
        self.cursor_config_path = self._get_cursor_config_path()

    def _is_command_available(self) -> bool:
        """Check if jira-mcp command is available in PATH.

        Returns:
            True if command is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["jira-mcp", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _get_cursor_config_path(self) -> Path:
        """Get Cursor config path for current OS.

        Returns:
            Path to Cursor's mcp_settings.json file

        Raises:
            FileNotFoundError: If Cursor config location cannot be determined
        """
        system = platform.system()
        home = Path.home()

        if system == "Darwin":  # macOS
            return home / ".cursor" / "mcp_settings.json"
        elif system == "Windows":
            return home / "AppData" / "Roaming" / "Cursor" / "User" / "mcp_settings.json"
        else:  # Linux and others
            return home / ".config" / "Cursor" / "User" / "mcp_settings.json"

    def _create_backup(self) -> Optional[Path]:
        """Create backup of existing Cursor config.

        Returns:
            Path to backup file if created, None otherwise
        """
        if not self.cursor_config_path.exists():
            return None

        backup_path = self.cursor_config_path.with_suffix(".json.backup")

        try:
            shutil.copy2(self.cursor_config_path, backup_path)
            logger.info(f"Created backup at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    def _restore_backup(self, backup_path: Path) -> bool:
        """Restore from backup file.

        Args:
            backup_path: Path to backup file

        Returns:
            True if restored successfully, False otherwise
        """
        if not backup_path or not backup_path.exists():
            return False

        try:
            shutil.copy2(backup_path, self.cursor_config_path)
            logger.info("Restored from backup")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

    def _update_config(self, config: dict) -> dict:
        """Update config dict with jira-mcp entry.

        Args:
            config: Existing Cursor config dict

        Returns:
            Updated config dict
        """
        # Ensure mcpServers exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Add/update jira entry
        config_file_path = str(Path.home() / ".jira-mcp" / "config.json")
        config["mcpServers"]["jira"] = {
            "command": "jira-mcp",
            "args": ["serve", "--config", config_file_path],
        }

        return config

    def install(self) -> bool:
        """Install Jira MCP to Cursor's MCP settings.

        Creates backup before modifying. Restores backup on failure.

        Returns:
            True if installation succeeded, False otherwise
        """
        try:
            # Create config directory if needed
            self.cursor_config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create backup if config exists
            backup_path = self._create_backup()

            # Load existing config or create new
            if self.cursor_config_path.exists():
                try:
                    with open(self.cursor_config_path, "r") as f:
                        config = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in Cursor config, creating new config")
                    config = {}
            else:
                config = {}

            # Update config
            config = self._update_config(config)

            # Save updated config
            with open(self.cursor_config_path, "w") as f:
                json.dump(config, f, indent=2)

            logger.info("Successfully installed Jira MCP to Cursor")
            return True

        except Exception as e:
            logger.error(f"Installation failed: {e}")

            # Attempt to restore backup
            if backup_path:
                self._restore_backup(backup_path)

            return False

    def uninstall(self) -> bool:
        """Remove Jira MCP from Cursor's MCP settings.

        Returns:
            True if uninstallation succeeded, False otherwise
        """
        try:
            if not self.cursor_config_path.exists():
                logger.info("Cursor config not found, nothing to uninstall")
                return True

            # Load config
            with open(self.cursor_config_path, "r") as f:
                config = json.load(f)

            # Remove jira entry if exists
            if "mcpServers" in config and "jira" in config["mcpServers"]:
                del config["mcpServers"]["jira"]

                # Save updated config
                with open(self.cursor_config_path, "w") as f:
                    json.dump(config, f, indent=2)

                logger.info("Successfully uninstalled Jira MCP from Cursor")

            return True

        except Exception as e:
            logger.error(f"Uninstallation failed: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if Jira MCP is installed in Cursor.

        Returns:
            True if installed, False otherwise
        """
        if not self.cursor_config_path.exists():
            return False

        try:
            with open(self.cursor_config_path, "r") as f:
                config = json.load(f)

            return "mcpServers" in config and "jira" in config.get("mcpServers", {})

        except Exception:
            return False
