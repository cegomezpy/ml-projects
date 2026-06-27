"""
Application configuration using Pydantic Settings.

This allows configuration through environment variables or .env file.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings.

    These can be overridden with environment variables.
    """

    # Application
    app_name: str = "ML Projects API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Storage
    models_dir: str = "models"
    metadata_file: str = "models/metadata.json"

    # CORS
    cors_origins: list[str] = ["*"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
