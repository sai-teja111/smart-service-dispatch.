from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from modules.notifications_service import (
    get_recipient_details,
    serialize_notification,
    get_notifications,
    mark_notification_as_read,
    create_notification,
)


USER_UUID = uuid4()
NOTIFICATION_UUID = uuid4()
REQUEST_UUID = uuid4()


def make_user(role="customer", user_uuid=USER_UUID):
    return {
        "user_uuid": str(user_uuid),
        "role": role,
    }


def make_notification(is_read=False):
    return SimpleNamespace(
        notification_uuid=NOTIFICATION_UUID,
        recipient_uuid=USER_UUID,
        recipient_role="customer",
        title="Service update",
        message="Your service request was updated.",
        notification_type="STATUS_UPDATE",
        request_uuid=REQUEST_UUID,
        is_read=is_read,
        created_at=datetime(2026, 10, 12, tzinfo=timezone.utc),
        read_at=None,
    )


def make_session():
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = False
    return session


# ---------------------------------------------------------
# get_recipient_details
# ---------------------------------------------------------

def test_get_recipient_details_from_user_uuid():
    user_uuid, role = get_recipient_details(make_user())

    assert user_uuid == USER_UUID
    assert role == "customer"


def test_get_recipient_details_from_sub():
    user = {
        "sub": str(USER_UUID),
        "role": "technician",
    }

    user_uuid, role = get_recipient_details(user)

    assert user_uuid == USER_UUID
    assert role == "technician"


def test_get_recipient_details_from_object():
    user = SimpleNamespace(
        sub=str(USER_UUID),
        user_uuid=None,
        role="technician",
    )

    user_uuid, role = get_recipient_details(user)

    assert user_uuid == USER_UUID
    assert role == "technician"


@pytest.mark.parametrize(
    "user",
    [
        {},
        {"user_uuid": str(USER_UUID)},
        {"user_uuid": str(USER_UUID), "role": "admin"},
        {"user_uuid": None, "role": "customer"},
    ],
)
def test_get_recipient_details_rejects_invalid_user(user):
    with pytest.raises(HTTPException) as exc:
        get_recipient_details(user)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid authenticated user."


@pytest.mark.parametrize("invalid_uuid", ["not-a-uuid", None])
def test_get_recipient_details_rejects_invalid_uuid(invalid_uuid):
    user = {
        "user_uuid": invalid_uuid,
        "role": "customer",
    }

    if invalid_uuid is None:
        with pytest.raises(HTTPException) as exc:
            get_recipient_details(user)

        assert exc.value.status_code == 401
        return

    with pytest.raises(HTTPException) as exc:
        get_recipient_details(user)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid authenticated user UUID."


# ---------------------------------------------------------
# serialize_notification
# ---------------------------------------------------------

def test_serialize_notification():
    notification = make_notification()

    result = serialize_notification(notification)

    assert result == {
        "notification_uuid": NOTIFICATION_UUID,
        "title": "Service update",
        "message": "Your service request was updated.",
        "notification_type": "STATUS_UPDATE",
        "request_uuid": REQUEST_UUID,
        "is_read": False,
        "created_at": notification.created_at,
        "read_at": None,
    }


# ---------------------------------------------------------
# get_notifications
# ---------------------------------------------------------

@patch("modules.notifications_service.get_session_context")
def test_get_notifications_returns_notifications(mock_context):
    session = make_session()
    mock_context.return_value = session

    unread = make_notification(is_read=False)
    read = make_notification(is_read=True)

    session.exec.return_value.all.return_value = [unread, read]

    result = get_notifications(make_user())

    assert result["count"] == 2
    assert result["unread_count"] == 1
    assert len(result["notifications"]) == 2
    assert result["notifications"][0]["is_read"] is False
    assert result["notifications"][1]["is_read"] is True


@patch("modules.notifications_service.get_session_context")
def test_get_notifications_returns_empty_result(mock_context):
    session = make_session()
    mock_context.return_value = session
    session.exec.return_value.all.return_value = []

    result = get_notifications(make_user())

    assert result == {
        "count": 0,
        "unread_count": 0,
        "notifications": [],
    }


@patch("modules.notifications_service.get_session_context")
def test_get_notifications_database_error(mock_context):
    mock_context.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(HTTPException) as exc:
        get_notifications(make_user())

    assert exc.value.status_code == 500
    assert exc.value.detail == "Unable to fetch notifications."


def test_get_notifications_invalid_user():
    with pytest.raises(HTTPException) as exc:
        get_notifications({"role": "admin"})

    assert exc.value.status_code == 401


# ---------------------------------------------------------
# mark_notification_as_read
# ---------------------------------------------------------

@patch("modules.notifications_service.get_session_context")
def test_mark_notification_as_read_success(mock_context):
    session = make_session()
    mock_context.return_value = session

    notification = make_notification(is_read=False)
    session.exec.return_value.first.return_value = notification

    result = mark_notification_as_read(
        NOTIFICATION_UUID,
        make_user(),
    )

    assert result["message"] == "Notification marked as read."
    assert notification.is_read is True
    assert notification.read_at is not None
    assert notification.read_at.tzinfo is not None

    session.add.assert_called_once_with(notification)
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(notification)


@patch("modules.notifications_service.get_session_context")
def test_mark_notification_already_read_does_not_commit(mock_context):
    session = make_session()
    mock_context.return_value = session

    notification = make_notification(is_read=True)
    notification.read_at = datetime(2026, 10, 11, tzinfo=timezone.utc)
    original_read_at = notification.read_at

    session.exec.return_value.first.return_value = notification

    result = mark_notification_as_read(
        NOTIFICATION_UUID,
        make_user(),
    )

    assert result["message"] == "Notification marked as read."
    assert notification.read_at == original_read_at

    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.refresh.assert_not_called()


@patch("modules.notifications_service.get_session_context")
def test_mark_notification_not_found(mock_context):
    session = make_session()
    mock_context.return_value = session
    session.exec.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        mark_notification_as_read(
            NOTIFICATION_UUID,
            make_user(),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Notification not found."


@patch("modules.notifications_service.get_session_context")
def test_mark_notification_database_error(mock_context):
    session = make_session()
    mock_context.return_value = session
    session.exec.side_effect = RuntimeError("Database failure")

    with pytest.raises(HTTPException) as exc:
        mark_notification_as_read(
            NOTIFICATION_UUID,
            make_user(),
        )

    assert exc.value.status_code == 500
    assert exc.value.detail == "Unable to update notification."


def test_mark_notification_invalid_user():
    with pytest.raises(HTTPException) as exc:
        mark_notification_as_read(
            NOTIFICATION_UUID,
            {"role": "admin"},
        )

    assert exc.value.status_code == 401


# ---------------------------------------------------------
# create_notification
# ---------------------------------------------------------

@patch("modules.notifications_service.get_session_context")
def test_create_notification_success(mock_context):
    session = make_session()
    mock_context.return_value = session

    result = create_notification(
        recipient_uuid=USER_UUID,
        recipient_role="customer",
        title="Service update",
        message="Your request has been updated.",
        notification_type="STATUS_UPDATE",
        request_uuid=REQUEST_UUID,
    )

    assert result is None
    session.add.assert_called_once()
    session.commit.assert_called_once()

    notification = session.add.call_args.args[0]

    assert notification.recipient_uuid == USER_UUID
    assert notification.recipient_role == "customer"
    assert notification.title == "Service update"
    assert notification.message == "Your request has been updated."
    assert notification.notification_type == "STATUS_UPDATE"
    assert notification.request_uuid == REQUEST_UUID


@pytest.mark.parametrize("role", ["admin", "manager", "", None])
def test_create_notification_rejects_invalid_role(role):
    with pytest.raises(
        ValueError,
        match="Invalid notification recipient role.",
    ):
        create_notification(
            recipient_uuid=USER_UUID,
            recipient_role=role,
            title="Title",
            message="Message",
            notification_type="INFO",
        )


@patch("modules.notifications_service.get_session_context")
def test_create_notification_without_request_uuid(mock_context):
    session = make_session()
    mock_context.return_value = session

    create_notification(
        recipient_uuid=USER_UUID,
        recipient_role="technician",
        title="New assignment",
        message="A request was assigned to you.",
        notification_type="ASSIGNMENT",
    )

    notification = session.add.call_args.args[0]

    assert notification.recipient_role == "technician"
    assert notification.request_uuid is None


@patch("modules.notifications_service.get_session_context")
def test_create_notification_database_error(mock_context):
    session = make_session()
    mock_context.return_value = session
    session.commit.side_effect = RuntimeError("Commit failed")

    with pytest.raises(RuntimeError, match="Commit failed"):
        create_notification(
            recipient_uuid=USER_UUID,
            recipient_role="customer",
            title="Title",
            message="Message",
            notification_type="INFO",
        )
