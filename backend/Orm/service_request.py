import uuid
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class ServiceRequest(SQLModel, table=True):

    __tablename__ = "service_requests"

    request_id: int | None = Field(
        default=None,
        primary_key=True
    )

    request_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True
    )

    customer_id: int = Field(
        foreign_key="customers.customer_id"
    )

    skill_id: int = Field(
        foreign_key="skills.skill_id"
    )

    problem_description: str

    priority: str | None = Field(
        default=None,
        max_length=20
    )

    assigned_technician_id: int | None = Field(
        default=None,
        foreign_key="technicians.technician_id"
    )

    status: str = Field(
        default="OPEN",
        max_length=30
    )

    request_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )