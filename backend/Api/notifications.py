from uuid import UUID

from fastapi import APIRouter, Depends

from Api.dependencies import get_current_user
from modules.notifications_service import (
    get_notifications as fetch_notifications,
    mark_notification_as_read as update_notification_read_status,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("")
def get_notifications(
    current_user=Depends(get_current_user),
):
    """Get notifications for the authenticated user."""

    return fetch_notifications(current_user)


@router.patch("/{notification_uuid}/read")
def mark_notification_as_read(
    notification_uuid: UUID,
    current_user=Depends(get_current_user),
):
    """Mark the authenticated user's notification as read."""

    return update_notification_read_status(
        notification_uuid=notification_uuid,
        current_user=current_user,
    )