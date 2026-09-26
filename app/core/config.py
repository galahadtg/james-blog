"""Application configuration using Pydantic Settings.

Loads configuration from environment variables and .env file.
All settings are validated at startup.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_platform"

    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS - allow all origins during development
    CORS_ORIGINS: list[str] = ["*"]

    # API
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "James Blog"
    PROJECT_VERSION: str = "0.1.0"

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: list[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".mp4", ".mov", ".avi",
        ".mp3", ".wav",
        ".zip", ".tar", ".gz",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
