
import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR.parent / ".env"


class Settings(BaseSettings):
    """Application configuration."""

    app_name: str = "Smart Service Dispatch System"
    debug: bool = False

    database_url: str = Field(
        validation_alias="DATABASE_URL",
    )

    secret_key: str = Field(
        validation_alias="JWT_SECRET_KEY",
    )

    openrouter_api_key: str = Field(
        validation_alias="OPENROUTER_API_KEY",
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        validation_alias="CORS_ORIGINS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        """Accept a JSON array or comma-separated origin list."""

        if value is None:
            return [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return []

            if value.startswith("["):
                value = json.loads(value)
            else:
                value = value.split(",")

        if not isinstance(value, list):
            raise ValueError(
                "CORS_ORIGINS must be a JSON array or comma-separated string."
            )

        return [
            origin.strip().rstrip("/")
            for origin in value
            if isinstance(origin, str) and origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Create and cache the settings object."""
    return Settings()
