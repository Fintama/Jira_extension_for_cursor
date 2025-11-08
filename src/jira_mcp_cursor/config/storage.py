"""Secure encrypted storage for configuration."""

import json
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Any


class SecureConfig:
    """Encrypted configuration storage."""

    def __init__(self):
        self.config_dir = Path.home() / ".jira-mcp"
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / ".key"

        # Generate or load encryption key
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key based on machine ID."""
        if self.key_file.exists():
            return self.key_file.read_bytes()

        # Generate new key
        key = Fernet.generate_key()

        self.config_dir.mkdir(exist_ok=True, parents=True)
        self.key_file.write_bytes(key)
        self.key_file.chmod(0o600)  # Owner read/write only

        return key

    def save(self, config: dict[str, Any]) -> None:
        """Save encrypted configuration."""
        json_data = json.dumps(config).encode()
        encrypted = self.cipher.encrypt(json_data)

        self.config_dir.mkdir(exist_ok=True, parents=True)
        self.config_file.write_bytes(encrypted)
        self.config_file.chmod(0o600)

    def load(self) -> dict[str, Any]:
        """Load and decrypt configuration."""
        if not self.config_file.exists():
            return {}

        encrypted = self.config_file.read_bytes()
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted)

    def delete(self) -> None:
        """Delete configuration."""
        if self.config_file.exists():
            self.config_file.unlink()
        if self.key_file.exists():
            self.key_file.unlink()

    def exists(self) -> bool:
        """Check if configuration file exists.

        Returns:
            True if config file exists, False otherwise
        """
        return self.config_file.exists()

    def validate(self) -> bool:
        """Validate that stored configuration is complete.

        Checks that all required fields are present:
        - jira_url
        - email and api_token (for Cloud) OR username and password (for Server)

        Returns:
            True if config is complete and valid, False otherwise

        Example:
            >>> storage = SecureConfig()
            >>> storage.save({"jira_url": "https://test.atlassian.net",
            ...               "email": "user@example.com",
            ...               "api_token": "token123"})
            >>> storage.validate()
            True
        """
        if not self.exists():
            return False

        config = self.load()

        # Check required fields
        if not config.get("jira_url"):
            return False

        # Check auth fields (Cloud or Server)
        has_cloud_auth = bool(config.get("email") and config.get("api_token"))
        has_server_auth = bool(config.get("username") and config.get("password"))

        return has_cloud_auth or has_server_auth

    def get_validation_errors(self) -> list[str]:
        """Get list of validation errors for current config.

        Returns:
            List of error messages, empty if config is valid
        """
        errors = []

        if not self.exists():
            errors.append("Configuration file does not exist")
            return errors

        config = self.load()

        # Check required fields
        if not config.get("jira_url"):
            errors.append("Missing required field: jira_url")

        # Check auth fields
        has_cloud_auth = bool(config.get("email") and config.get("api_token"))
        has_server_auth = bool(config.get("username") and config.get("password"))

        if not (has_cloud_auth or has_server_auth):
            errors.append(
                "Missing authentication: provide (email + api_token) or (username + password)"
            )

        return errors
