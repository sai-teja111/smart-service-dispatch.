from Log_config import log

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from Api.role_dependencies import require_customer
from Api.dependencies import get_current_user

from Api.schemas import (
    FeedbackCreateResponse,
    FeedbackViewResponse
)

from modules.feedback_service import (
    create_feedback as create_feedback_service,
    get_feedback,
    CustomerNotFoundError,
    ServiceRequestNotFoundError,
    UnauthorizedFeedbackError,
    IncompleteServiceError,
    NoTechnicianAssignedError,
    FeedbackAlreadyExistsError,
    TechnicianNotFoundError,
    InvalidUserRoleError
)


logger = log()


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


class FeedbackCreate(BaseModel):

    request_uuid: str

    rating: float = Field(
        ge=1,
        le=5
    )

    comments: str | None = None


# ============================================================
# CREATE FEEDBACK
# ============================================================

@router.post(
    "",
    response_model=FeedbackCreateResponse
)
def create_feedback(
    data: FeedbackCreate,
    current_user=Depends(require_customer)
):
    logger.info(
        "Create feedback attempt | "
        "customer_uuid: %s | request_uuid: %s | rating: %s",
        current_user["user_uuid"],
        data.request_uuid,
        data.rating
    )

    try:
        feedback = create_feedback_service(
            customer_uuid=current_user["user_uuid"],
            request_uuid=data.request_uuid,
            rating=data.rating,
            comments=data.comments
        )

        logger.info(
            "Feedback created successfully | "
            "customer_uuid: %s | request_uuid: %s | rating: %s",
            current_user["user_uuid"],
            data.request_uuid,
            data.rating
        )

        return feedback

    except CustomerNotFoundError as error:
        logger.warning(
            "Feedback creation failed - customer not found | "
            "customer_uuid: %s | request_uuid: %s | reason: %s",
            current_user["user_uuid"],
            data.request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except ServiceRequestNotFoundError as error:
        logger.warning(
            "Feedback creation failed - service request not found | "
            "request_uuid: %s | reason: %s",
            data.request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except UnauthorizedFeedbackError as error:
        logger.warning(
            "Unauthorized feedback attempt | "
            "customer_uuid: %s | request_uuid: %s | reason: %s",
            current_user["user_uuid"],
            data.request_uuid,
            error
        )

        raise HTTPException(
            status_code=403,
            detail=str(error)
        )

    except IncompleteServiceError as error:
        logger.warning(
            "Feedback rejected because service is incomplete | "
            "request_uuid: %s | reason: %s",
            data.request_uuid,
            error
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except NoTechnicianAssignedError as error:
        logger.warning(
            "Feedback rejected because no technician is assigned | "
            "request_uuid: %s | reason: %s",
            data.request_uuid,
            error
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except FeedbackAlreadyExistsError as error:
        logger.warning(
            "Duplicate feedback rejected | "
            "customer_uuid: %s | request_uuid: %s | reason: %s",
            current_user["user_uuid"],
            data.request_uuid,
            error
        )

        raise HTTPException(
            status_code=409,
            detail=str(error)
        )

    except TechnicianNotFoundError as error:
        logger.warning(
            "Feedback creation failed - technician not found | "
            "request_uuid: %s | reason: %s",
            data.request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# ============================================================
# VIEW FEEDBACK
# ============================================================

@router.get(
    "/{request_uuid}",
    response_model=FeedbackViewResponse
)
def view_feedback(
    request_uuid: str,
    current_user=Depends(get_current_user)
):
    logger.info(
        "View feedback attempt | "
        "user_uuid: %s | role: %s | request_uuid: %s",
        current_user["user_uuid"],
        current_user["role"],
        request_uuid
    )

    try:
        feedback = get_feedback(
            user_uuid=current_user["user_uuid"],
            role=current_user["role"],
            request_uuid=request_uuid
        )

        logger.info(
            "Feedback retrieved successfully | "
            "user_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            request_uuid
        )

        return feedback

    except ServiceRequestNotFoundError as error:
        logger.warning(
            "Feedback retrieval failed - service request not found | "
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
            "Feedback retrieval failed - customer not found | "
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
            "Feedback retrieval failed - technician not found | "
            "user_uuid: %s | request_uuid: %s | reason: %s",
            current_user["user_uuid"],
            request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except UnauthorizedFeedbackError as error:
        logger.warning(
            "Unauthorized feedback access | "
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
            "Invalid user role for feedback access | "
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
