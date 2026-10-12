from Log_config import log

from  fastapi import APIRouter, Depends, HTTPException

from Api.dependencies import get_current_user

from Api.schemas import ReportsResponse

from modules.reports_service import get_reports


logger = log()


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# ============================================================
# VIEW REPORTS
# ============================================================

@router.get(
    "",
    response_model=ReportsResponse
)
def view_reports(
    current_user=Depends(get_current_user)
):

    logger.info(
        "View reports attempt | "
        "user_uuid: %s | role: %s",
        current_user["user_uuid"],
        current_user["role"]
    )

    if current_user["role"] != "technician":

        logger.warning(
            "View reports denied | "
            "user_uuid: %s | role: %s",
            current_user["user_uuid"],
            current_user["role"]
        )

        raise HTTPException(
            status_code=403,
            detail="Only technicians can view reports."
        )

    reports = get_reports()

    logger.info(
        "Reports retrieved successfully | "
        "technician_uuid: %s",
        current_user["user_uuid"]
    )

    return reports