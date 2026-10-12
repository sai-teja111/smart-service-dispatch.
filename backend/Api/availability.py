from Log_config import log

from  fastapi import APIRouter, Depends, HTTPException
from  pydantic import BaseModel, Field

from Api.dependencies import get_current_user

from Api.schemas import (
    TechnicianAvailabilityUpdateResponse,
    TechnicianAvailabilityResponse
)

from modules.availability_service import (
    update_technician_availability,
    get_technician_availability,
    TechnicianNotFoundError,
    SameAvailabilityError,
    InvalidAvailabilityError
)


logger = log()


router = APIRouter(
    prefix="/technician",
    tags=["Technician Availability"]
)


class AvailabilityUpdate(BaseModel):

    availability: str = Field(
        min_length=1
    )


# ============================================================
# UPDATE TECHNICIAN AVAILABILITY
# ============================================================

@router.patch(
    "/availability",
    response_model=TechnicianAvailabilityUpdateResponse
)
def update_availability(
    data: AvailabilityUpdate,
    current_user=Depends(get_current_user)
):

    logger.info(
        "Update technician availability attempt | "
        "technician_uuid: %s | requested_availability: %s",
        current_user["user_uuid"],
        data.availability
    )

    if current_user["role"] != "technician":

        logger.warning(
            "Update technician availability denied | "
            "user_uuid: %s | role: %s",
            current_user["user_uuid"],
            current_user["role"]
        )

        raise HTTPException(
            status_code=403,
            detail="Only technicians can update availability."
        )

    try:

        result = update_technician_availability(
            technician_uuid=current_user["user_uuid"],
            availability=data.availability
        )

        logger.info(
            "Technician availability updated successfully | "
            "technician_uuid: %s | availability: %s",
            current_user["user_uuid"],
            data.availability
        )

        return result

    except InvalidAvailabilityError as error:

        logger.warning(
            "Invalid technician availability | "
            "technician_uuid: %s | requested_availability: %s | reason: %s",
            current_user["user_uuid"],
            data.availability,
            error
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except TechnicianNotFoundError as error:

        logger.warning(
            "Technician not found while updating availability | "
            "technician_uuid: %s | reason: %s",
            current_user["user_uuid"],
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except SameAvailabilityError as error:

        logger.warning(
            "Technician availability unchanged | "
            "technician_uuid: %s | availability: %s | reason: %s",
            current_user["user_uuid"],
            data.availability,
            error
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ============================================================
# VIEW TECHNICIAN AVAILABILITY
# ============================================================

@router.get(
    "/availability",
    response_model=TechnicianAvailabilityResponse
)
def view_availability(
    current_user=Depends(get_current_user)
):

    logger.info(
        "View technician availability attempt | "
        "user_uuid: %s | role: %s",
        current_user["user_uuid"],
        current_user["role"]
    )

    if current_user["role"] != "technician":

        logger.warning(
            "View technician availability denied | "
            "user_uuid: %s | role: %s",
            current_user["user_uuid"],
            current_user["role"]
        )

        raise HTTPException(
            status_code=403,
            detail="Only technicians can view their availability."
        )

    try:

        result = get_technician_availability(
            technician_uuid=current_user["user_uuid"]
        )

        logger.info(
            "Technician availability retrieved successfully | "
            "technician_uuid: %s",
            current_user["user_uuid"]
        )

        return result

    except TechnicianNotFoundError as error:

        logger.warning(
            "Technician not found while viewing availability | "
            "technician_uuid: %s | reason: %s",
            current_user["user_uuid"],
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )