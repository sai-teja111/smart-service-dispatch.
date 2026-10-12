import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field
from pydantic import field_validator


class Customer(SQLModel, table=True):

    __tablename__ = "customers"

    customer_id: int | None = Field(
        default=None,
        primary_key=True
    )

    customer_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True
    )

    customer_name: str = Field(
        max_length=100
    )

    phone: str = Field(
        max_length=10,
        unique=True
    )

    password_hash: str = Field(
        max_length=255
    )

    city: str = Field(
        max_length=50
    )

    area: str = Field(
        max_length=100
    )

    pincode: str = Field(
        max_length=10
    )

    # Stores the most recent successful login time.
    # None means no login has been recorded yet.
    last_login_at: datetime | None = Field(
        default=None,
        nullable=True
    )

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, value):

        value = value.strip()

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Customer name must contain only letters."
            )

        return value.title()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):

        value = value.strip()

        if not value.isdigit() or len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits."
            )

        return value

    @field_validator("city")
    @classmethod
    def validate_city(cls, value):

        value = value.strip().lower()

        if value != "hyderabad":
            raise ValueError(
                "Currently, service is available only in Hyderabad."
            )

        return "Hyderabad"

    @field_validator("area")
    @classmethod
    def validate_area(cls, value):

        value = value.strip()

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Area must contain only letters."
            )

        return value.title()

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value):

        value = value.strip()

        if not value.isdigit() or len(value) != 6:
            raise ValueError(
                "Pincode must contain exactly 6 digits."
            )

        return value
