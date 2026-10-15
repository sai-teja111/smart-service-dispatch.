import re
import uuid
from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel, Field


class Admin(SQLModel, table=True):

    __tablename__ = "admins"

    admin_id: int | None = Field(
        default=None,
        primary_key=True,
    )

    admin_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True,
        index=True,
    )

    admin_name: str = Field(
        max_length=100,
    )

    email: str = Field(
        max_length=254,
        unique=True,
        index=True,
    )

    password_hash: str = Field(
        max_length=255,
    )

    is_active: bool = Field(
        default=True,
        nullable=False,
    )

    last_login_at: datetime | None = Field(
        default=None,
        nullable=True,
    )

    @field_validator("admin_name")
    @classmethod
    def validate_admin_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Admin name is required.")

        if len(value) > 100:
            raise ValueError(
                "Admin name cannot exceed 100 characters."
            )

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Admin name must contain only letters and spaces."
            )

        return value.title()

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()

        if len(value) > 254:
            raise ValueError(
                "Email cannot exceed 254 characters."
            )

        email_pattern = (
            r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
            r"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}"
            r"[A-Za-z0-9])?"
            r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}"
            r"[A-Za-z0-9])?)+$"
        )

        if not re.fullmatch(email_pattern, value):
            raise ValueError(
                "Enter a valid email address."
            )

        return value
