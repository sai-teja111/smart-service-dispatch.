from uuid import uuid4
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from Api.dependencies import get_current_user

from modules.availability_service import (
    update_technician_availability,
    get_technician_availability,
    TechnicianNotFoundError,
    SameAvailabilityError,
    InvalidAvailabilityError,
)

from tests.mocks.session_mock import SessionMock


client = TestClient(app)


# ============================================================
# COMMON TEST DATA
# ============================================================

technician_uuid = uuid4()


def technician_user():
    return {
        "user_uuid": str(technician_uuid),
        "role": "technician",
    }


def customer_user():
    return {
        "user_uuid": str(uuid4()),
        "role": "customer",
    }


def make_technician(availability="Available"):
    return SimpleNamespace(
        technician_id=10,
        technician_uuid=technician_uuid,
        technician_name="Test Technician",
        availability=availability,
    )


def make_session():
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = False
    return session


def first_result(value):
    result = MagicMock()
    result.first.return_value = value
    result.all.return_value = []
    return result


# ============================================================
# CLEAN DEPENDENCY OVERRIDES
# ============================================================

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


# ============================================================
# API - UPDATE AVAILABILITY SUCCESS
# ============================================================

@patch("Api.availability.update_technician_availability")
def test_update_availability_success(mock_update):
    app.dependency_overrides[get_current_user] = technician_user

    mock_update.return_value = {
        "message": "Technician availability updated successfully.",
        "technician_uuid": technician_uuid,
        "old_availability": "Available",
        "new_availability": "Busy",
    }

    response = client.patch(
        "/technician/availability",
        json={"availability": "Busy"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Technician availability updated successfully."
    assert data["technician_uuid"] == str(technician_uuid)
    assert data["old_availability"] == "Available"
    assert data["new_availability"] == "Busy"

    mock_update.assert_called_once_with(
        technician_uuid=str(technician_uuid),
        availability="Busy",
    )


# ============================================================
# API - UPDATE AVAILABILITY WRONG ROLE
# ============================================================

def test_update_availability_wrong_role():
    app.dependency_overrides[get_current_user] = customer_user

    response = client.patch(
        "/technician/availability",
        json={"availability": "Busy"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Only technicians can update availability."
    )


# ============================================================
# API - UPDATE INVALID AVAILABILITY
# ============================================================

@patch("Api.availability.update_technician_availability")
def test_update_availability_invalid(mock_update):
    app.dependency_overrides[get_current_user] = technician_user

    mock_update.side_effect = InvalidAvailabilityError(
        "Availability must be Available, Busy or Unavailable."
    )

    response = client.patch(
        "/technician/availability",
        json={"availability": "Holiday"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Availability must be Available, Busy or Unavailable."
    )


# ============================================================
# API - TECHNICIAN NOT FOUND
# ============================================================

@patch("Api.availability.update_technician_availability")
def test_update_availability_technician_not_found(mock_update):
    app.dependency_overrides[get_current_user] = technician_user

    mock_update.side_effect = TechnicianNotFoundError(
        "Technician not found."
    )

    response = client.patch(
        "/technician/availability",
        json={"availability": "Busy"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Technician not found."


# ============================================================
# API - SAME AVAILABILITY
# ============================================================

@patch("Api.availability.update_technician_availability")
def test_update_availability_same(mock_update):
    app.dependency_overrides[get_current_user] = technician_user

    mock_update.side_effect = SameAvailabilityError(
        "Technician already has this availability status."
    )

    response = client.patch(
        "/technician/availability",
        json={"availability": "Available"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Technician already has this availability status."
    )


# ============================================================
# API - EMPTY AVAILABILITY
# ============================================================

def test_update_availability_empty():
    app.dependency_overrides[get_current_user] = technician_user

    response = client.patch(
        "/technician/availability",
        json={"availability": ""},
    )

    assert response.status_code == 422


# ============================================================
# API - VIEW AVAILABILITY SUCCESS
# ============================================================

@patch("Api.availability.get_technician_availability")
def test_view_availability_success(mock_get):
    app.dependency_overrides[get_current_user] = technician_user

    mock_get.return_value = {
        "technician_uuid": technician_uuid,
        "availability": "Busy",
    }

    response = client.get("/technician/availability")

    assert response.status_code == 200

    data = response.json()

    assert data["technician_uuid"] == str(technician_uuid)
    assert data["availability"] == "Busy"

    mock_get.assert_called_once_with(
        technician_uuid=str(technician_uuid),
    )


# ============================================================
# API - VIEW AVAILABILITY WRONG ROLE
# ============================================================

def test_view_availability_wrong_role():
    app.dependency_overrides[get_current_user] = customer_user

    response = client.get("/technician/availability")

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Only technicians can view their availability."
    )


# ============================================================
# API - VIEW AVAILABILITY TECHNICIAN NOT FOUND
# ============================================================

@patch("Api.availability.get_technician_availability")
def test_view_availability_not_found(mock_get):
    app.dependency_overrides[get_current_user] = technician_user

    mock_get.side_effect = TechnicianNotFoundError(
        "Technician not found."
    )

    response = client.get("/technician/availability")

    assert response.status_code == 404
    assert response.json()["detail"] == "Technician not found."


# ============================================================
# SERVICE - INVALID AVAILABILITY
# ============================================================

@patch("modules.availability_service.get_session_context")
def test_update_availability_invalid_service(mock_get_session):
    with pytest.raises(InvalidAvailabilityError):
        update_technician_availability(
            technician_uuid,
            "Holiday",
        )

    mock_get_session.assert_not_called()


# ============================================================
# SERVICE - TECHNICIAN NOT FOUND
# ============================================================

@patch("modules.availability_service.get_session_context")
def test_update_availability_not_found_service(mock_get_session):
    session = make_session()
    session.exec.return_value = first_result(None)
    mock_get_session.return_value.__enter__.return_value = session

    with pytest.raises(TechnicianNotFoundError):
        update_technician_availability(
            technician_uuid,
            "Busy",
        )


# ============================================================
# SERVICE - SAME AVAILABILITY
# ============================================================

@patch("modules.availability_service.get_session_context")
def test_update_availability_same_service(mock_get_session):
    session = make_session()
    session.exec.return_value = first_result(
        make_technician("Available")
    )
    mock_get_session.return_value.__enter__.return_value = session

    with pytest.raises(SameAvailabilityError):
        update_technician_availability(
            technician_uuid,
            "available",
        )

    session.commit.assert_not_called()


# ============================================================
# SERVICE - UPDATE SUCCESS
# ============================================================

@patch("modules.availability_service.get_session_context")
def test_update_availability_success_service(mock_get_session):
    technician = make_technician("Available")

    session = make_session()
    session.exec.return_value = first_result(technician)
    mock_get_session.return_value.__enter__.return_value = session

    result = update_technician_availability(
        technician_uuid,
        "  busy  ",
    )

    assert result["message"] == (
        "Technician availability updated successfully."
    )
    assert result["technician_uuid"] == technician_uuid
    assert result["old_availability"] == "Available"
    assert result["new_availability"] == "Busy"
    assert technician.availability == "Busy"

    session.add.assert_called_once_with(technician)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(technician)


# ============================================================
# SERVICE - UPDATE TO UNAVAILABLE
# ============================================================

@patch("modules.availability_service.get_session_context")
def test_update_availability_to_unavailable(mock_get_session):
    technician = make_technician("Busy")

    session = make_session()
    session.exec.return_value = first_result(technician)
    mock_get_session.return_value.__enter__.return_value = session

    result = update_technician_availability(
        technician_uuid,
        "unavailable",
    )

    assert result["old_availability"] == "Busy"
    assert result["new_availability"] == "Unavailable"
    assert technician.availability == "Unavailable"


# ============================================================
# SERVICE - GET AVAILABILITY NOT FOUND
# ============================================================

@patch("modules.availability_service.get_session_context")
def test_get_availability_not_found_service(mock_get_session):
    session = make_session()
    session.exec.return_value = first_result(None)
    mock_get_session.return_value.__enter__.return_value = session

    with pytest.raises(TechnicianNotFoundError):
        get_technician_availability(technician_uuid)


# ============================================================
# SERVICE - GET AVAILABILITY SUCCESS
# ============================================================

@patch("modules.availability_service.get_session_context")
def test_get_availability_success_service(mock_get_session):
    technician = make_technician("Busy")

    session = make_session()
    session.exec.return_value = first_result(technician)
    mock_get_session.return_value.__enter__.return_value = session

    result = get_technician_availability(technician_uuid)

    assert result["technician_uuid"] == technician_uuid
    assert result["availability"] == "Busy"


# ============================================================
# SESSION MOCK TESTS
# ============================================================

def test_result_mock_all_with_data():
    session = SessionMock(result=["row1", "row2"])
    result = session.exec("query")

    assert result.all() == ["row1", "row2"]


def test_session_mock_get():
    expected = object()
    session = SessionMock(get_result=expected)

    assert session.get("Model", 1) is expected


def test_session_mock_results_mode():
    session = SessionMock(
        results=["first result", "second result"]
    )

    result1 = session.exec("query1")
    result2 = session.exec("query2")

    assert result1.first() == "first result"
    assert result2.first() == "second result"
    assert session.exec_count == 2


def test_session_mock_context_and_methods():
    session = SessionMock()

    with session as active_session:
        assert active_session is session
        assert session.add("object") is None
        assert session.commit() is None
        assert session.refresh("object") is None


def test_session_mock_empty_result():
    session = SessionMock()
    result = session.exec("query")

    assert result.first() is None
    assert result.all() == []
