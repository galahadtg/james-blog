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
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Platform"
    PROJECT_VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
