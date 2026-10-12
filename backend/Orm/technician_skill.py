from  sqlmodel import SQLModel, Field


class TechnicianSkill(SQLModel, table=True):

    __tablename__ = "technician_skills"

    technician_id: int = Field(
        primary_key=True,
        foreign_key="technicians.technician_id"
    )

    skill_id: int = Field(
        primary_key=True,
        foreign_key="skills.skill_id"
    )

    experience_years: int | None = Field(
        default=None
    )

    expertise_level: str | None = Field(
        default=None,
        max_length=20
    )

    is_verified: bool = Field(
        default=True
    )