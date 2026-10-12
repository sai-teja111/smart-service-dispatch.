import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    NoDecode,
)
from typing import Annotated


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR.parent / ".env"


class Settings(BaseSettings):
    """Application configuration."""

    app_name: str = "Smart Service Dispatch System"
    debug: bool = False

    database_url: str = Field(validation_alias="DATABASE_URL")
    secret_key: str = Field(validation_alias="JWT_SECRET_KEY")
    openrouter_api_key: str = Field(
        validation_alias="OPENROUTER_API_KEY"
    )

    cors_origins: Annotated[list[str], NoDecode] = Field(
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

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return []

            if value.startswith("["):
                return json.loads(value)

            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]

        return value

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Create and cache application settings."""
    return Settings()