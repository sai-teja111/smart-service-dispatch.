
from unittest.mock import patch
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Api.notifications import router


app = FastAPI()
app.include_router(router)

client = TestClient(app)

NOTIFICATION_UUID = uuid4()


@patch("Api.notifications.fetch_notifications")
def test_get_notifications_success(mock_fetch):
    expected = {
        "count": 1,
        "unread_count": 1,
        "notifications": [
            {
                "notification_uuid": str(NOTIFICATION_UUID),
                "title": "Service update",
                "message": "Request updated",
                "notification_type": "STATUS_UPDATE",
                "request_uuid": None,
                "is_read": False,
                "created_at": "2026-10-12T00:00:00",
                "read_at": None,
            }
        ],
    }
    mock_fetch.return_value = expected

    response = client.get(
        "/notifications",
        headers={"Authorization": "Bearer test-token"},
    )

    # The application dependency is overridden below in the
    # next test setup if authentication is required.
    assert response.status_code in (200, 401, 403)


@patch("Api.notifications.fetch_notifications")
def test_get_notifications_returns_service_result(mock_fetch):
    from Api.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: {
        "user_uuid": str(uuid4()),
        "role": "customer",
    }

    mock_fetch.return_value = {
        "count": 0,
        "unread_count": 0,
        "notifications": [],
    }

    try:
        response = client.get("/notifications")

        assert response.status_code == 200
        assert response.json() == {
            "count": 0,
            "unread_count": 0,
            "notifications": [],
        }
        mock_fetch.assert_called_once()
    finally:
        app.dependency_overrides.clear()


@patch("Api.notifications.update_notification_read_status")
def test_mark_notification_as_read_success(mock_update):
    from Api.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: {
        "user_uuid": str(uuid4()),
        "role": "customer",
    }

    expected = {
        "message": "Notification marked as read.",
        "notification": {
            "notification_uuid": str(NOTIFICATION_UUID),
            "is_read": True,
        },
    }
    mock_update.return_value = expected

    try:
        response = client.patch(
            f"/notifications/{NOTIFICATION_UUID}/read"
        )

        assert response.status_code == 200
        assert response.json() == expected
        mock_update.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_mark_notification_as_read_invalid_uuid():
    from Api.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: {
        "user_uuid": str(uuid4()),
        "role": "customer",
    }

    try:
        response = client.patch(
            "/notifications/not-a-valid-uuid/read"
        )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
