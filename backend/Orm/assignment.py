import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import SQLModel, Field


class Assignment(SQLModel, table=True):

    __tablename__ = "assignments"

    assignment_id: int | None = Field(
        default=None,
        primary_key=True
    )

    assignment_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True
    )

    request_id: int = Field(
        foreign_key="service_requests.request_id"
    )

    technician_id: int = Field(
        foreign_key="technicians.technician_id"
    )

    assignment_score: Decimal | None = Field(
        default=None,
        max_digits=5,
        decimal_places=2
    )

    assigned_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )