from  sqlmodel import select

from Orm.database import get_session_context
from Orm.technician import Technician


class TechnicianNotFoundError(Exception):
    pass


class SameAvailabilityError(Exception):
    pass


class InvalidAvailabilityError(Exception):
    pass


ALLOWED_AVAILABILITY = [
    "Available",
    "Busy",
    "Unavailable"
]


def update_technician_availability(
    technician_uuid,
    availability
):
    new_availability = availability.strip().title()

    if new_availability not in ALLOWED_AVAILABILITY:
        raise InvalidAvailabilityError(
            "Availability must be Available, "
            "Busy or Unavailable."
        )

    with get_session_context() as session:

        technician = session.exec(
            select(Technician).where(
                Technician.technician_uuid == technician_uuid
            )
        ).first()

        if not technician:
            raise TechnicianNotFoundError(
                "Technician not found."
            )

        old_availability = technician.availability

        if old_availability == new_availability:
            raise SameAvailabilityError(
                "Technician already has this "
                "availability status."
            )

        technician.availability = new_availability

        session.add(technician)

        session.commit()

        session.refresh(technician)

        return {
            "message": (
                "Technician availability "
                "updated successfully."
            ),
            "technician_uuid": technician.technician_uuid,
            "old_availability": old_availability,
            "new_availability": technician.availability
        }


def get_technician_availability(technician_uuid):

    with get_session_context() as session:

        technician = session.exec(
            select(Technician).where(
                Technician.technician_uuid == technician_uuid
            )
        ).first()

        if not technician:
            raise TechnicianNotFoundError(
                "Technician not found."
            )

        return {
            "technician_uuid": technician.technician_uuid,
            "availability": technician.availability
        }