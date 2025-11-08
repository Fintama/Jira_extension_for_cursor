"""Application settings and configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Jira Connection
    jira_url: str = ""  # Will be loaded from .env or encrypted config
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None
    jira_username: Optional[str] = None
    jira_password: Optional[str] = None

    # Optional Configuration
    jira_project_key: Optional[str] = None  # Default project for operations
    jira_user_domain: Optional[str] = None  # Default domain for user searches (e.g., "@fintama.com")
    jira_max_results: int = 50
    jira_timeout: int = 30
    jira_max_retries: int = 3  # Maximum retry attempts for failed requests

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def is_cloud(self) -> bool:
        """Determine if using Jira Cloud or Server."""
        return self.jira_email is not None and self.jira_api_token is not None

    def get_auth(self) -> tuple[str, str]:
        """Get authentication credentials."""
        if self.is_cloud:
            if not self.jira_email or not self.jira_api_token:
                raise ValueError("Jira Cloud requires email and API token")
            return (self.jira_email, self.jira_api_token)
        else:
            if not self.jira_username or not self.jira_password:
                raise ValueError("Jira Server requires username and password")
            return (self.jira_username, self.jira_password)


# Global settings instance (lazy loaded)
_settings = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# For backward compatibility
settings = get_settings()
