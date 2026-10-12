from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select

from Log_config import log
from Orm.database import get_session_context
from Orm.notifications import Notification


logger = log()


def get_recipient_details(current_user):
    """Extract and validate the authenticated user's identity."""

    if isinstance(current_user, dict):
        user_uuid = (
            current_user.get("sub")
            or current_user.get("user_uuid")
        )
        role = current_user.get("role")
    else:
        user_uuid = (
            getattr(current_user, "sub", None)
            or getattr(current_user, "user_uuid", None)
        )
        role = getattr(current_user, "role", None)

    if not user_uuid or role not in {"customer", "technician"}:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        user_uuid = UUID(str(user_uuid))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user UUID.",
        )

    return user_uuid, role


def serialize_notification(notification: Notification) -> dict:
    """Convert a notification model into an API-friendly dictionary."""

    return {
        "notification_uuid": notification.notification_uuid,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "request_uuid": notification.request_uuid,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
        "read_at": notification.read_at,
    }


def get_notifications(current_user) -> dict:
    """Retrieve notifications belonging to the authenticated user."""

    recipient_uuid, recipient_role = get_recipient_details(
        current_user
    )

    logger.info(
        "Fetching notifications | role: %s | user_uuid: %s",
        recipient_role,
        recipient_uuid,
    )

    try:
        with get_session_context() as session:
            statement = (
                select(Notification)
                .where(
                    Notification.recipient_uuid == recipient_uuid,
                    Notification.recipient_role == recipient_role,
                )
                .order_by(Notification.created_at.desc())
            )

            notifications = session.exec(statement).all()

            unread_count = sum(
                1 for notification in notifications
                if not notification.is_read
            )

            logger.info(
                "Notifications fetched | total: %s | unread: %s",
                len(notifications),
                unread_count,
            )

            return {
                "count": len(notifications),
                "unread_count": unread_count,
                "notifications": [
                    serialize_notification(notification)
                    for notification in notifications
                ],
            }

    except Exception:
        logger.exception(
            "Failed to fetch notifications | user_uuid: %s",
            recipient_uuid,
        )
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch notifications.",
        )


def mark_notification_as_read(
    notification_uuid: UUID,
    current_user,
) -> dict:
    """Mark a notification as read if it belongs to the current user."""

    recipient_uuid, recipient_role = get_recipient_details(
        current_user
    )

    logger.info(
        "Marking notification as read | notification_uuid: %s",
        notification_uuid,
    )

    try:
        with get_session_context() as session:
            statement = select(Notification).where(
                Notification.notification_uuid == notification_uuid,
                Notification.recipient_uuid == recipient_uuid,
                Notification.recipient_role == recipient_role,
            )

            notification = session.exec(statement).first()

            if notification is None:
                raise HTTPException(
                    status_code=404,
                    detail="Notification not found.",
                )

            if not notification.is_read:
                notification.is_read = True
                notification.read_at = datetime.now(timezone.utc)

                session.add(notification)
                session.commit()
                session.refresh(notification)

            logger.info(
                "Notification marked as read | notification_uuid: %s",
                notification_uuid,
            )

            return {
                "message": "Notification marked as read.",
                "notification": serialize_notification(notification),
            }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Failed to mark notification as read | notification_uuid: %s",
            notification_uuid,
        )
        raise HTTPException(
            status_code=500,
            detail="Unable to update notification.",
        )
def create_notification(
    recipient_uuid: UUID,
    recipient_role: str,
    title: str,
    message: str,
    notification_type: str,
    request_uuid: UUID | None = None,
) -> None:
    """Create and persist a notification."""

    if recipient_role not in {"customer", "technician"}:
        raise ValueError("Invalid notification recipient role.")

    logger.info(
        "Creating notification | role: %s | user_uuid: %s | type: %s",
        recipient_role,
        recipient_uuid,
        notification_type,
    )

    try:
        with get_session_context() as session:
            notification = Notification(
                recipient_uuid=recipient_uuid,
                recipient_role=recipient_role,
                title=title,
                message=message,
                notification_type=notification_type,
                request_uuid=request_uuid,
            )

            session.add(notification)
            session.commit()

            logger.info(
                "Notification created | notification_uuid: %s",
                notification.notification_uuid,
            )

    except Exception:
        logger.exception(
            "Failed to create notification | role: %s | user_uuid: %s",
            recipient_role,
            recipient_uuid,
        )
        raise