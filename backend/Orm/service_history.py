import uuid
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class ServiceHistory(SQLModel, table=True):

    __tablename__ = "service_history"

    history_id: int | None = Field(
        default=None,
        primary_key=True
    )

    history_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True
    )

    request_id: int = Field(
        foreign_key="service_requests.request_id"
    )

    old_status: str | None = Field(
        default=None,
        max_length=30
    )

    new_status: str | None = Field(
        default=None,
        max_length=30
    )

    updated_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    remarks: str | None = Field(
        default=None
    )