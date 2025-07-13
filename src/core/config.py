"""
Core configuration management for the Virtual Assistant.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseSettings, Field


class Environment(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)

    # Application
    app_name: str = Field(default="Virtual Assistant")
    app_version: str = Field(default="1.0.0")

    # Voice Settings
    wake_word: str = Field(default="hey assistant")
    voice_language: str = Field(default="en-US")
    voice_recognition_timeout: int = Field(default=5)
    voice_synthesis_rate: int = Field(default=200)

    # API Settings
    api_host: str = Field(default="localhost")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=False)

    # Database Settings
    database_url: str = Field(default="postgresql://localhost/virtual_assistant")
    redis_url: str = Field(default="redis://localhost:6379")

    # Security Settings
    secret_key: str = Field(default="your-secret-key-change-this")
    encryption_key: Optional[str] = Field(default=None)
    session_timeout: int = Field(default=3600)  # 1 hour

    # Logging Settings
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/virtual_assistant.log")

    # Email Settings
    default_email_client: str = Field(default="outlook")

    # IDE Settings
    default_ide: str = Field(default="vscode")
    code_templates_path: str = Field(default="templates/code")

    # File Paths
    user_data_path: str = Field(default="data/users")
    temp_path: str = Field(default="temp")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class ConfigManager:
    """Configuration manager for loading and managing settings."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.settings = self._load_settings()

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        env = os.getenv("ENVIRONMENT", "development")
        return f"config/{env}.yaml"

    def _load_settings(self) -> Settings:
        """Load settings from configuration file and environment."""
        config_data = {}

        # Load from YAML file if exists
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as file:
                config_data = yaml.safe_load(file) or {}

        # Merge with environment variables
        return Settings(**config_data)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        return getattr(self.settings, key, default)

    def update_setting(self, key: str, value: Any) -> None:
        """Update a setting value."""
        setattr(self.settings, key, value)

    def save_settings(self) -> None:
        """Save current settings to configuration file."""
        config_data = self.settings.dict()

        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        with open(self.config_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(config_data, file, default_flow_style=False)


# Global configuration instance
config_manager = ConfigManager()
settings = config_manager.settings
