from Log_config import log

from  fastapi import APIRouter, Depends, HTTPException

from Api.dependencies import get_current_user

from Api.schemas import ServiceRequestHistoryResponse

from modules.history_service import (
    get_service_history,
    ServiceRequestNotFoundError,
    CustomerNotFoundError,
    TechnicianNotFoundError,
    UnauthorizedServiceHistoryError,
    InvalidUserRoleError
)


logger = log()


router = APIRouter(
    prefix="/service-history",
    tags=["Service History"]
)


@router.get(
    "/{request_uuid}",
    response_model=ServiceRequestHistoryResponse
)
def view_service_history(
    request_uuid: str,
    current_user=Depends(get_current_user)
):

    logger.info(
        "View service history attempt | "
        "user_uuid: %s | role: %s | request_uuid: %s",
        current_user["user_uuid"],
        current_user["role"],
        request_uuid
    )

    try:

        history = get_service_history(
            request_uuid=request_uuid,
            user_uuid=current_user["user_uuid"],
            role=current_user["role"]
        )

        logger.info(
            "Service history retrieved successfully | "
            "user_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            request_uuid
        )

        return history

    except ServiceRequestNotFoundError as error:

        logger.warning(
            "Service request not found while viewing history | "
            "request_uuid: %s | reason: %s",
            request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except CustomerNotFoundError as error:

        logger.warning(
            "Customer not found while viewing service history | "
            "user_uuid: %s | request_uuid: %s | reason: %s",
            current_user["user_uuid"],
            request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except TechnicianNotFoundError as error:

        logger.warning(
            "Technician not found while viewing service history | "
            "user_uuid: %s | request_uuid: %s | reason: %s",
            current_user["user_uuid"],
            request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except UnauthorizedServiceHistoryError as error:

        logger.warning(
            "Unauthorized service history access | "
            "user_uuid: %s | role: %s | request_uuid: %s | reason: %s",
            current_user["user_uuid"],
            current_user["role"],
            request_uuid,
            error
        )

        raise HTTPException(
            status_code=403,
            detail=str(error)
        )

    except InvalidUserRoleError as error:

        logger.warning(
            "Invalid user role for service history | "
            "user_uuid: %s | role: %s | request_uuid: %s | reason: %s",
            current_user["user_uuid"],
            current_user["role"],
            request_uuid,
            error
        )

        raise HTTPException(
            status_code=403,
            detail=str(error)
        )