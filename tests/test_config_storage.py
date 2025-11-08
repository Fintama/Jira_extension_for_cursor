"""Tests for secure configuration storage."""

import pytest
from cryptography.fernet import Fernet, InvalidToken
from jira_mcp_cursor.config.storage import SecureConfig


@pytest.mark.ci_critical
def test_save_and_load_config(tmp_path):
    """CI: Test encrypting and decrypting config - round-trip."""
    # Create SecureConfig with temp directory
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    # Generate new key for this test
    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)
    storage.key_file.write_bytes(storage.key)

    config = {
        "jira_url": "https://test.atlassian.net",
        "email": "test@example.com",
        "api_token": "secret-token-123",
    }

    storage.save(config)
    loaded = storage.load()

    assert loaded == config
    assert loaded["api_token"] == "secret-token-123"


def test_config_file_permissions(tmp_path):
    """Test that config file has correct permissions (600)."""
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)

    config = {"jira_url": "https://test.atlassian.net"}

    storage.save(config)

    # Check config file permissions (owner read/write only)
    assert storage.config_file.stat().st_mode & 0o777 == 0o600
    # Key file permissions are set when created, verified in save method


def test_validate_complete_config(tmp_path):
    """Test validation passes for complete config."""
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    # Initialize encryption
    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)
    storage.key_file.parent.mkdir(parents=True, exist_ok=True)
    storage.key_file.write_bytes(storage.key)

    complete_config = {
        "jira_url": "https://test.atlassian.net",
        "email": "test@example.com",
        "api_token": "token-123",
    }

    storage.save(complete_config)

    # validate() should return True for complete config
    result = storage.validate()
    assert result is True


def test_validate_incomplete_config(tmp_path):
    """Test validation fails for incomplete config."""
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    # Initialize encryption
    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)
    storage.key_file.parent.mkdir(parents=True, exist_ok=True)
    storage.key_file.write_bytes(storage.key)

    incomplete_config = {
        "jira_url": "https://test.atlassian.net",
        # Missing email and api_token
    }

    storage.save(incomplete_config)

    # validate() should return False for incomplete config
    result = storage.validate()
    assert result is False


def test_load_nonexistent_config(tmp_path):
    """Edge case: Loading config when file doesn't exist."""
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)

    # Load without saving first
    loaded = storage.load()

    assert loaded == {}


def test_corrupted_config_file(tmp_path):
    """Edge case: Handle corrupted/invalid encrypted file."""
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)

    # Write corrupted data to config file
    storage.config_file.write_bytes(b"corrupted-data-not-encrypted")

    # Should handle gracefully
    with pytest.raises(InvalidToken):
        storage.load()


def test_save_with_special_characters(tmp_path):
    """Edge case: Save config with special characters in values."""
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)

    config = {
        "jira_url": "https://test.atlassian.net",
        "email": "test+special@example.com",
        "api_token": "T0k3n!@#$%^&*()_+-=[]{}|;:,.<>?",
    }

    storage.save(config)
    loaded = storage.load()

    assert loaded == config
    assert loaded["api_token"] == "T0k3n!@#$%^&*()_+-=[]{}|;:,.<>?"


def test_exists_method(tmp_path):
    """Test exists() method to check if config file exists."""
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)

    # Should not exist initially
    assert storage.exists() is False

    # Save config
    storage.save({"jira_url": "https://test.atlassian.net"})

    # Should exist now
    assert storage.exists() is True


def test_delete_config(tmp_path):
    """Test deleting configuration."""
    storage = SecureConfig()
    storage.config_dir = tmp_path
    storage.config_file = tmp_path / "config.json"
    storage.key_file = tmp_path / ".key"

    storage.key = Fernet.generate_key()
    storage.cipher = Fernet(storage.key)
    storage.key_file.write_bytes(storage.key)

    # Save config
    storage.save({"jira_url": "https://test.atlassian.net"})
    assert storage.config_file.exists()

    # Delete
    storage.delete()

    # Should be gone
    assert not storage.config_file.exists()
    assert not storage.key_file.exists()
