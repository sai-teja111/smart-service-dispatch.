import uuid
from  datetime import datetime
from  decimal import Decimal

from  sqlmodel import SQLModel, Field


class Feedback(SQLModel, table=True):

    __tablename__ = "feedback"

    feedback_id: int | None = Field(
        default=None,
        primary_key=True
    )

    feedback_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True
    )

    request_id: int = Field(
        foreign_key="service_requests.request_id"
    )

    customer_id: int = Field(
        foreign_key="customers.customer_id"
    )

    technician_id: int = Field(
        foreign_key="technicians.technician_id"
    )

    rating: Decimal | None = Field(
        default=None,
        max_digits=2,
        decimal_places=1
    )

    comments: str | None = Field(
        default=None
    )

    feedback_date: datetime = Field(
        default_factory=datetime.now
    )