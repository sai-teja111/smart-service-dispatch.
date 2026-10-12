import uuid

from  sqlmodel import SQLModel, Field


class Skill(SQLModel, table=True):

    __tablename__ = "skills"

    skill_id: int | None = Field(
        default=None,
        primary_key=True
    )

    skill_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True
    )

    skill_name: str = Field(
        max_length=100,
        unique=True
    )

    category: str = Field(
        max_length=50
    )

    difficulty_level: str | None = Field(
        default=None,
        max_length=20
    )

    estimated_duration: int | None = Field(
        default=None
    )

    description: str | None = Field(
        default=None
    )