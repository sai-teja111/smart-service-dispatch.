import re

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class AdminProvision(BaseModel):
    """Input schema for securely provisioning an admin account."""

    admin_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr = Field(
        max_length=254,
    )

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    @field_validator("admin_name")
    @classmethod
    def validate_admin_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Admin name is required.")

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Admin name must contain only letters and spaces."
            )

        return value.title()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError(
                "Password must not exceed 72 UTF-8 bytes."
            )

        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one digit."
            )

        if not re.search(r"[^A-Za-z0-9]", value):
            raise ValueError(
                "Password must contain at least one special character."
            )

        return value


class AdminLogin(BaseModel):
    """Input schema for admin login."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(
        max_length=254,
    )

    password: str = Field(
        min_length=1,
        max_length=72,
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError(
                "Password must not exceed 72 UTF-8 bytes."
            )

        return value
