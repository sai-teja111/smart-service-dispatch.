from Log_config import log

from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException
)

from pydantic import BaseModel, Field

from Api.schemas import (
    ServiceDetectionStageResponse,
    ServiceRequestCreateResponse,
    CustomerServiceRequestListResponse,
    ServiceRequestHistoryResponse,
    CustomerServiceRequestResponse,
    TechnicianStatusUpdateResponse
)

from Api.role_dependencies import (
    require_customer,
    require_technician,
)

from modules.service_request_service import (
    detect_service,
    create_service_request as create_service_request_service,
    get_customer_service_requests,
    get_customer_service_request,
    get_service_request_history,
    get_customer_uuid_for_request,
    update_service_request_status as update_service_request_status_service,
    CustomerNotFoundError,
    TechnicianNotFoundError,
    ServiceRequestNotFoundError,
    UnauthorizedServiceRequestError,
    DuplicateServiceRequestError,
    InvalidServiceRequestStatusError
)

from modules.notifications_service import create_notification


logger = log()


router = APIRouter(
    prefix="/service-requests",
    tags=["Service Requests2"]
)


# ============================================================
# BACKGROUND TASK — SERVICE REQUEST CREATED
# ============================================================

def service_request_background_task(
    customer_uuid,
    request_uuid,
    technician_uuid=None,
    technician_name=None
):
    # CUSTOMER NOTIFICATION

    create_notification(
        recipient_uuid=UUID(str(customer_uuid)),
        recipient_role="customer",
        title="Service Request Created",
        message=(
            "Your service request has been created successfully."
        ),
        notification_type="SERVICE_REQUEST_CREATED",
        request_uuid=UUID(str(request_uuid))
    )

    logger.info(
        "Customer notification created | "
        "customer_uuid: %s | request_uuid: %s",
        customer_uuid,
        request_uuid
    )

    # TECHNICIAN NOTIFICATION

    if technician_uuid:

        create_notification(
            recipient_uuid=UUID(str(technician_uuid)),
            recipient_role="technician",
            title="New Service Assignment",
            message=(
                "A new service request has been assigned to you. "
                "Please review the request details and update "
                "its status accordingly."
            ),
            notification_type="SERVICE_REQUEST_ASSIGNED",
            request_uuid=UUID(str(request_uuid))
        )

        logger.info(
            "Technician notification created | "
            "technician_uuid: %s | request_uuid: %s",
            technician_uuid,
            request_uuid
        )


# ============================================================
# BACKGROUND TASK — SERVICE REQUEST STATUS UPDATED
# ============================================================

def service_status_notification_task(
    customer_uuid,
    technician_uuid,
    request_uuid,
    new_status
):
    # CUSTOMER NOTIFICATION

    create_notification(
        recipient_uuid=UUID(str(customer_uuid)),
        recipient_role="customer",
        title="Service Request Status Updated",
        message=(
            f"Your service request status has been updated "
            f"to {new_status}."
        ),
        notification_type="SERVICE_REQUEST_STATUS_UPDATED",
        request_uuid=UUID(str(request_uuid))
    )

    logger.info(
        "Customer status notification created | "
        "customer_uuid: %s | request_uuid: %s | status: %s",
        customer_uuid,
        request_uuid,
        new_status
    )

    # TECHNICIAN CONFIRMATION NOTIFICATION

    create_notification(
        recipient_uuid=UUID(str(technician_uuid)),
        recipient_role="technician",
        title="Service Request Updated Successfully",
        message=(
            f"You have successfully updated the service "
            f"request status to {new_status}."
        ),
        notification_type="SERVICE_REQUEST_STATUS_UPDATED",
        request_uuid=UUID(str(request_uuid))
    )

    logger.info(
        "Technician status confirmation notification created | "
        "technician_uuid: %s | request_uuid: %s | status: %s",
        technician_uuid,
        request_uuid,
        new_status
    )


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class ServiceRequestCreate(BaseModel):

    problem_description: str = Field(
        min_length=1
    )

    skill_id: int | None = None

    priority: str = Field(
        default="Low"
    )


class ServiceRequestStatusUpdate(BaseModel):

    status: str = Field(
        min_length=1
    )

    remarks: str | None = None


# ============================================================
# CREATE / DETECT SERVICE REQUEST
# ============================================================

@router.post(
    "",
    response_model=(
        ServiceDetectionStageResponse
        | ServiceRequestCreateResponse
    )
)
def create_service_request(
    data: ServiceRequestCreate,
    background_tasks: BackgroundTasks,
    current_user=Depends(require_customer)
):
    logger.info(
        "Service request operation attempt | "
        "customer_uuid: %s | skill_id: %s",
        current_user["user_uuid"],
        data.skill_id
    )


    try:

        # STAGE 1 — SERVICE DETECTION

        if data.skill_id is None:

            logger.info(
                "Service detection started | "
                "customer_uuid: %s",
                current_user["user_uuid"]
            )

            detection = detect_service(
                customer_uuid=current_user["user_uuid"],
                problem_description=data.problem_description
            )

            # SERVICE DETECTED

            if detection["skill_id"] is not None:

                logger.info(
                    "Service detected successfully | "
                    "customer_uuid: %s | skill_id: %s | "
                    "service: %s | match_type: %s",
                    current_user["user_uuid"],
                    detection["skill_id"],
                    detection["skill_name"],
                    detection["match_type"]
                )

                return {
                    "message": (
                        "Service detected successfully. "
                        "Please confirm the detected service "
                        "or select another service."
                    ),
                    "service_detection": {
                        "skill_id": detection["skill_id"],
                        "skill_name": detection["skill_name"],
                        "category": detection["category"],
                        "match_type": detection["match_type"],
                        "distance": detection["distance"]
                    },
                    "available_services": []
                }

            # SERVICE NOT DETECTED

            logger.info(
                "Service could not be detected. "
                "Returning available services | "
                "customer_uuid: %s",
                current_user["user_uuid"]
            )

            return {
                "message": (
                    "Service could not be automatically "
                    "detected. Please select a service."
                ),
                "service_detection": None,
                "available_services": (
                    detection["available_services"]
                )
            }

        # STAGE 2 — CREATE SERVICE REQUEST

        logger.info(
            "Service request creation started | "
            "customer_uuid: %s | skill_id: %s",
            current_user["user_uuid"],
            data.skill_id
        )

        service_request = create_service_request_service(
            customer_uuid=current_user["user_uuid"],
            problem_description=data.problem_description,
            skill_id=data.skill_id,
            priority=data.priority
        )

        logger.info(
            "Service request created successfully | "
            "customer_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            service_request.get("request_uuid")
        )

        # ADD NOTIFICATION BACKGROUND TASK

        technician = service_request.get("technician")

        background_tasks.add_task(
            service_request_background_task,
            current_user["user_uuid"],
            service_request["request_uuid"],
            technician.get("technician_uuid") if technician else None,
            technician.get("technician_name") if technician else None
        )

        return service_request

    except CustomerNotFoundError as error:

        logger.warning(
            "Customer not found | "
            "customer_uuid: %s | reason: %s",
            current_user["user_uuid"],
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except DuplicateServiceRequestError as error:

        logger.warning(
            "Duplicate service request rejected | "
            "customer_uuid: %s | reason: %s",
            current_user["user_uuid"],
            error
        )

        raise HTTPException(
            status_code=409,
            detail=str(error)
        )

    except ValueError as error:

        logger.warning(
            "Invalid service request data | "
            "customer_uuid: %s | reason: %s",
            current_user["user_uuid"],
            error
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ============================================================
# VIEW CUSTOMER SERVICE REQUESTS
# ============================================================

@router.get(
    "",
    response_model=CustomerServiceRequestListResponse
)
def view_service_requests(
    current_user=Depends(require_customer)
):
    logger.info(
        "View service requests attempt | customer_uuid: %s",
        current_user["user_uuid"]
    )

    
    try:

        service_requests = get_customer_service_requests(
            current_user["user_uuid"]
        )

    except CustomerNotFoundError as error:

        logger.warning(
            "View service requests failed | "
            "customer_uuid: %s | reason: %s",
            current_user["user_uuid"],
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    if not service_requests:

        logger.info(
            "No service requests found | customer_uuid: %s",
            current_user["user_uuid"]
        )

        return {
            "count": 0,
            "service_requests": []
        }

    logger.info(
        "Service requests retrieved successfully | "
        "customer_uuid: %s | count: %s",
        current_user["user_uuid"],
        len(service_requests)
    )

    return {
        "count": len(service_requests),
        "service_requests": service_requests
    }


# ============================================================
# VIEW SERVICE REQUEST HISTORY
# ============================================================

@router.get(
    "/{request_uuid}/history",
    response_model=ServiceRequestHistoryResponse
)
def view_service_request_history(
    request_uuid: str,
    current_user=Depends(require_customer)
):
    logger.info(
        "View service request history attempt | "
        "customer_uuid: %s | request_uuid: %s",
        current_user["user_uuid"],
        request_uuid
    )

    

    try:

        history = get_service_request_history(
            customer_uuid=current_user["user_uuid"],
            request_uuid=request_uuid
        )

        logger.info(
            "Service request history retrieved successfully | "
            "customer_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            request_uuid
        )

        return history

    except CustomerNotFoundError as error:

        logger.warning(
            "Customer not found while viewing history | "
            "customer_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            request_uuid
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except ServiceRequestNotFoundError as error:

        logger.warning(
            "Service request history not found | "
            "request_uuid: %s | reason: %s",
            request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# ============================================================
# VIEW ONE CUSTOMER SERVICE REQUEST
# ============================================================

@router.get(
    "/{request_uuid}",
    response_model=CustomerServiceRequestResponse
)
def view_service_request(
    request_uuid: str,
    current_user=Depends(require_customer)
):
    logger.info(
        "View service request attempt | "
        "customer_uuid: %s | request_uuid: %s",
        current_user["user_uuid"],
        request_uuid
    )


    try:

        service_request = get_customer_service_request(
            customer_uuid=current_user["user_uuid"],
            request_uuid=request_uuid
        )

        logger.info(
            "Service request retrieved successfully | "
            "customer_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            request_uuid
        )

        return service_request

    except CustomerNotFoundError as error:

        logger.warning(
            "Customer not found while viewing service request | "
            "customer_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            request_uuid
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except ServiceRequestNotFoundError as error:

        logger.warning(
            "Service request not found | "
            "request_uuid: %s | reason: %s",
            request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# ============================================================
# UPDATE SERVICE REQUEST STATUS
# ============================================================

@router.patch(
    "/{request_uuid}/status",
    response_model=TechnicianStatusUpdateResponse
)
def update_service_request_status(
    request_uuid: str,
    data: ServiceRequestStatusUpdate,
    background_tasks: BackgroundTasks,
    current_user=Depends(require_technician)
):
    logger.info(
        "Update service request status attempt | "
        "technician_uuid: %s | request_uuid: %s | requested_status: %s",
        current_user["user_uuid"],
        request_uuid,
        data.status
    )

    try:

        result = update_service_request_status_service(
            technician_uuid=current_user["user_uuid"],
            request_uuid=request_uuid,
            requested_status=data.status,
            remarks=data.remarks
        )

        # GET CUSTOMER UUID

        customer_uuid = get_customer_uuid_for_request(
            request_uuid
        )

        # SCHEDULE CUSTOMER AND TECHNICIAN NOTIFICATIONS

        background_tasks.add_task(
            service_status_notification_task,
            customer_uuid,
            current_user["user_uuid"],
            result["request_uuid"],
            result["new_status"]
        )

        logger.info(
            "Service request status updated successfully | "
            "technician_uuid: %s | request_uuid: %s | status: %s",
            current_user["user_uuid"],
            request_uuid,
            result["new_status"]
        )

        return result

    except TechnicianNotFoundError as error:

        logger.warning(
            "Technician not found while updating status | "
            "technician_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            request_uuid
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except ServiceRequestNotFoundError as error:

        logger.warning(
            "Service request not found | "
            "request_uuid: %s | reason: %s",
            request_uuid,
            error
        )

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except UnauthorizedServiceRequestError as error:

        logger.warning(
            "Unauthorized service request status update | "
            "technician_uuid: %s | request_uuid: %s",
            current_user["user_uuid"],
            request_uuid
        )

        raise HTTPException(
            status_code=403,
            detail=str(error)
        )

    except InvalidServiceRequestStatusError as error:

        logger.warning(
            "Invalid service request status | "
            "request_uuid: %s | requested_status: %s | reason: %s",
            request_uuid,
            data.status,
            error
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )