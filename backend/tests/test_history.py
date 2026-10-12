from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from Api.dependencies import get_current_user

from modules.history_service import (
    get_service_history,
    ServiceRequestNotFoundError,
    CustomerNotFoundError,
    TechnicianNotFoundError,
    UnauthorizedServiceHistoryError,
    InvalidUserRoleError,
)


client = TestClient(app)

REQUEST_UUID = uuid4()
CUSTOMER_UUID = uuid4()
TECHNICIAN_UUID = uuid4()


# ============================================================
# COMMON TEST DATA
# ============================================================

def customer_user():
    return {
        "user_uuid": str(CUSTOMER_UUID),
        "role": "customer",
    }


def technician_user():
    return {
        "user_uuid": str(TECHNICIAN_UUID),
        "role": "technician",
    }


def invalid_user():
    return {
        "user_uuid": str(uuid4()),
        "role": "admin",
    }


def make_service_request(
    customer_id=1,
    technician_id=10,
    status="IN PROGRESS",
):
    return SimpleNamespace(
        request_id=100,
        request_uuid=REQUEST_UUID,
        customer_id=customer_id,
        assigned_technician_id=technician_id,
        status=status,
    )


def make_customer():
    return SimpleNamespace(
        customer_id=1,
        customer_uuid=CUSTOMER_UUID,
        customer_name="Test Customer",
    )


def make_technician():
    return SimpleNamespace(
        technician_id=10,
        technician_uuid=TECHNICIAN_UUID,
        technician_name="Test Technician",
    )


def make_history_record():
    return SimpleNamespace(
        old_status="PENDING",
        new_status="IN PROGRESS",
        updated_time=datetime.now(),
        remarks="Technician started the work.",
    )


def first_result(value):
    result = MagicMock()
    result.first.return_value = value
    result.all.return_value = []
    return result


def all_result(value):
    result = MagicMock()
    result.first.return_value = None
    result.all.return_value = value
    return result


def configure_session_context(session):
    context = MagicMock()
    context.__enter__.return_value = session
    context.__exit__.return_value = False
    return context


# ============================================================
# API TESTS
# ============================================================

@patch("Api.history.get_service_history")
def test_view_service_history_success(mock_get):
    app.dependency_overrides[get_current_user] = customer_user

    mock_get.return_value = {
        "request_uuid": REQUEST_UUID,
        "current_status": "IN PROGRESS",
        "count": 1,
        "history": [
            {
                "old_status": "PENDING",
                "new_status": "IN PROGRESS",
                "updated_time": datetime.now(),
                "remarks": "Technician started the work.",
            }
        ],
    }

    try:
        response = client.get(f"/service-history/{REQUEST_UUID}")

        assert response.status_code == 200
        data = response.json()
        assert data["request_uuid"] == str(REQUEST_UUID)
        assert data["count"] == 1
        assert len(data["history"]) == 1
        assert data["history"][0]["old_status"] == "PENDING"
        assert data["history"][0]["new_status"] == "IN PROGRESS"
        assert data["history"][0]["remarks"] == (
            "Technician started the work."
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.parametrize(
    "exception, status_code, message",
    [
        (
            ServiceRequestNotFoundError("Service request not found."),
            404,
            "Service request not found.",
        ),
        (
            CustomerNotFoundError("Customer not found."),
            404,
            "Customer not found.",
        ),
        (
            TechnicianNotFoundError("Technician not found."),
            404,
            "Technician not found.",
        ),
        (
            UnauthorizedServiceHistoryError(
                "You are not allowed to view this service history."
            ),
            403,
            "You are not allowed to view this service history.",
        ),
        (
            InvalidUserRoleError("Invalid user role."),
            403,
            "Invalid user role.",
        ),
    ],
)
def test_view_service_history_errors(exception, status_code, message):
    app.dependency_overrides[get_current_user] = customer_user

    with patch(
        "Api.history.get_service_history",
        side_effect=exception,
    ):
        try:
            response = client.get(f"/service-history/{REQUEST_UUID}")
            assert response.status_code == status_code
            assert response.json()["detail"] == message
        finally:
            app.dependency_overrides.pop(get_current_user, None)


# ============================================================
# SERVICE LAYER - REQUEST NOT FOUND
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_request_not_found(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)
    session.exec.return_value = first_result(None)

    with pytest.raises(
        ServiceRequestNotFoundError,
        match="Service request not found.",
    ):
        get_service_history(REQUEST_UUID, CUSTOMER_UUID, "customer")


# ============================================================
# SERVICE LAYER - CUSTOMER NOT FOUND
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_customer_not_found(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)

    session.exec.side_effect = [
        first_result(make_service_request()),
        first_result(None),
    ]

    with pytest.raises(
        CustomerNotFoundError,
        match="Customer not found.",
    ):
        get_service_history(REQUEST_UUID, CUSTOMER_UUID, "customer")


# ============================================================
# SERVICE LAYER - CUSTOMER UNAUTHORIZED
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_customer_unauthorized(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)

    different_customer = SimpleNamespace(customer_id=999)

    session.exec.side_effect = [
        first_result(make_service_request(customer_id=1)),
        first_result(different_customer),
    ]

    with pytest.raises(
        UnauthorizedServiceHistoryError,
        match="You are not allowed to view this service history.",
    ):
        get_service_history(REQUEST_UUID, CUSTOMER_UUID, "customer")


# ============================================================
# SERVICE LAYER - CUSTOMER NO HISTORY
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_customer_no_history(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)

    session.exec.side_effect = [
        first_result(make_service_request(customer_id=1)),
        first_result(make_customer()),
        all_result([]),
    ]

    result = get_service_history(REQUEST_UUID, CUSTOMER_UUID, "customer")

    assert result["request_uuid"] == REQUEST_UUID
    assert result["message"] == "No service history found."
    assert result["history"] == []
    assert "count" not in result


# ============================================================
# SERVICE LAYER - CUSTOMER WITH HISTORY
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_customer_success(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)

    session.exec.side_effect = [
        first_result(
            make_service_request(customer_id=1, status="IN PROGRESS")
        ),
        first_result(make_customer()),
        all_result([make_history_record()]),
    ]

    result = get_service_history(REQUEST_UUID, CUSTOMER_UUID, "customer")

    assert result["request_uuid"] == REQUEST_UUID
    assert result["current_status"] == "IN PROGRESS"
    assert result["count"] == 1
    assert result["history"][0]["old_status"] == "PENDING"
    assert result["history"][0]["new_status"] == "IN PROGRESS"
    assert result["history"][0]["remarks"] == (
        "Technician started the work."
    )


# ============================================================
# SERVICE LAYER - TECHNICIAN NOT FOUND
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_technician_not_found(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)

    session.exec.side_effect = [
        first_result(make_service_request()),
        first_result(None),
    ]

    with pytest.raises(
        TechnicianNotFoundError,
        match="Technician not found.",
    ):
        get_service_history(REQUEST_UUID, TECHNICIAN_UUID, "technician")


# ============================================================
# SERVICE LAYER - TECHNICIAN UNAUTHORIZED
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_technician_unauthorized(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)

    different_technician = SimpleNamespace(technician_id=999)

    session.exec.side_effect = [
        first_result(make_service_request(technician_id=10)),
        first_result(different_technician),
    ]

    with pytest.raises(
        UnauthorizedServiceHistoryError,
        match="You are not allowed to view this service history.",
    ):
        get_service_history(REQUEST_UUID, TECHNICIAN_UUID, "technician")


# ============================================================
# SERVICE LAYER - TECHNICIAN NO HISTORY
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_technician_no_history(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)

    session.exec.side_effect = [
        first_result(make_service_request(technician_id=10)),
        first_result(make_technician()),
        all_result([]),
    ]

    result = get_service_history(
        REQUEST_UUID,
        TECHNICIAN_UUID,
        "technician",
    )

    assert result["request_uuid"] == REQUEST_UUID
    assert result["message"] == "No service history found."
    assert result["history"] == []
    assert "count" not in result


# ============================================================
# SERVICE LAYER - TECHNICIAN WITH HISTORY
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_technician_success(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)

    session.exec.side_effect = [
        first_result(
            make_service_request(technician_id=10, status="COMPLETED")
        ),
        first_result(make_technician()),
        all_result([make_history_record()]),
    ]

    result = get_service_history(
        REQUEST_UUID,
        TECHNICIAN_UUID,
        "technician",
    )

    assert result["request_uuid"] == REQUEST_UUID
    assert result["current_status"] == "COMPLETED"
    assert result["count"] == 1
    assert result["history"][0]["new_status"] == "IN PROGRESS"


# ============================================================
# SERVICE LAYER - INVALID ROLE
# ============================================================

@patch("modules.history_service.get_session_context")
def test_get_history_invalid_role(mock_context):
    session = MagicMock()
    mock_context.return_value = configure_session_context(session)
    session.exec.return_value = first_result(make_service_request())

    with pytest.raises(
        InvalidUserRoleError,
        match="Invalid user role.",
    ):
        get_service_history(REQUEST_UUID, uuid4(), "admin")
