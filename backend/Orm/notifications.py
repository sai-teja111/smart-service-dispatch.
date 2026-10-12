
import uuid

from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class Notification(SQLModel, table=True):

    __tablename__ = "notifications"

    notification_id: int | None = Field(
        default=None,
        primary_key=True
    )

    notification_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True,
        index=True
    )

    recipient_uuid: uuid.UUID = Field(
        index=True
    )

    recipient_role: str = Field(
        max_length=20,
        index=True
    )

    title: str = Field(
        max_length=150
    )

    message: str = Field(
        max_length=500
    )

    notification_type: str = Field(
        max_length=50
    )

    request_uuid: uuid.UUID | None = Field(
        default=None,
        index=True
    )

    is_read: bool = Field(
        default=False,
        index=True
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    read_at: datetime | None = Field(
        default=None
    )
