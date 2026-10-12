from Log_config import log

from  fastapi import APIRouter, Depends, HTTPException

from Api.dependencies import get_current_user

from Api.schemas import (
    TechnicianServiceRequestResponse,
    TechnicianServiceRequestListResponse
)

from modules.technician_service import (
    get_assigned_service_requests,
    get_assigned_service_request
)


logger = log()


router = APIRouter(
    prefix="/technician",
    tags=["Technician"]
)


# ============================================================
# VIEW ASSIGNED SERVICE REQUESTS
# ============================================================

@router.get(
    "/service-requests",
    response_model=TechnicianServiceRequestListResponse
)
def view_assigned_service_requests(
    current_user=Depends(get_current_user)
):

    logger.info(
        "View assigned service requests attempt | "
        "technician_uuid: %s",
        current_user["user_uuid"]
    )

    # ========================================================
    # CHECK TECHNICIAN ROLE
    # ========================================================

    if current_user["role"] != "technician":

        logger.warning(
            "View assigned service requests denied | "
            "user_uuid: %s | role: %s",
            current_user["user_uuid"],
            current_user["role"]
        )

        raise HTTPException(
            status_code=403,
            detail=(
                "Only technicians can view "
                "assigned service requests."
            )
        )

    # ========================================================
    # GET ASSIGNED SERVICE REQUESTS
    # ========================================================

    service_requests = get_assigned_service_requests(
        current_user["user_uuid"]
    )

    # ========================================================
    # TECHNICIAN NOT FOUND
    # ========================================================

    if service_requests is None:

        logger.warning(
            "Technician not found while retrieving "
            "assigned service requests | technician_uuid: %s",
            current_user["user_uuid"]
        )

        raise HTTPException(
            status_code=404,
            detail="Technician not found."
        )

    # ========================================================
    # NO ASSIGNED REQUESTS
    # ========================================================

    if not service_requests:

        logger.info(
            "No assigned service requests found | "
            "technician_uuid: %s",
            current_user["user_uuid"]
        )

        return {
            "count": 0,
            "service_requests": []
        }

    logger.info(
        "Assigned service requests retrieved successfully | "
        "technician_uuid: %s | count: %s",
        current_user["user_uuid"],
        len(service_requests)
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "count": len(service_requests),
        "service_requests": service_requests
    }


# ============================================================
# VIEW ONE ASSIGNED SERVICE REQUEST
# ============================================================

@router.get(
    "/service-requests/{request_uuid}",
    response_model=TechnicianServiceRequestResponse
)
def view_assigned_service_request(
    request_uuid: str,
    current_user=Depends(get_current_user)
):

    logger.info(
        "View assigned service request attempt | "
        "technician_uuid: %s | request_uuid: %s",
        current_user["user_uuid"],
        request_uuid
    )

    # ========================================================
    # CHECK TECHNICIAN ROLE
    # ========================================================

    if current_user["role"] != "technician":

        logger.warning(
            "View assigned service request denied | "
            "user_uuid: %s | role: %s | request_uuid: %s",
            current_user["user_uuid"],
            current_user["role"],
            request_uuid
        )

        raise HTTPException(
            status_code=403,
            detail=(
                "Only technicians can view "
                "assigned service requests."
            )
        )

    # ========================================================
    # GET ASSIGNED SERVICE REQUEST
    # ========================================================

    service_request = get_assigned_service_request(
        current_user["user_uuid"],
        request_uuid
    )

    # ========================================================
    # REQUEST NOT FOUND
    # ========================================================

    if service_request is None:

        logger.warning(
            "Assigned service request not found | "
            "technician_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            request_uuid
        )

        raise HTTPException(
            status_code=404,
            detail="Assigned service request not found."
        )

    logger.info(
        "Assigned service request retrieved successfully | "
        "technician_uuid: %s | request_uuid: %s",
        current_user["user_uuid"],
        request_uuid
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return service_request