from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app
from Api.dependencies import get_current_user

from modules.technician_service import (
    get_assigned_service_requests,
    get_assigned_service_request,
)

from tests.mocks.session_mock import SessionMock


client = TestClient(app)


# ============================================================
# COMMON TEST DATA
# ============================================================

technician_uuid = uuid4()
request_uuid = uuid4()
customer_uuid = uuid4()
skill_uuid = uuid4()


def technician_user():
    return {
        "user_uuid": str(technician_uuid),
        "role": "technician",
    }


def customer_user():
    return {
        "user_uuid": str(customer_uuid),
        "role": "customer",
    }


def make_technician():
    return SimpleNamespace(
        technician_id=10,
        technician_uuid=technician_uuid,
        technician_name="Test Technician",
    )


def make_skill():
    return SimpleNamespace(
        skill_id=1,
        skill_uuid=skill_uuid,
        skill_name="AC Repair",
    )


def make_customer():
    return SimpleNamespace(
        customer_id=1,
        customer_uuid=customer_uuid,
        customer_name="Test Customer",
        phone="9876543210",
        city="Hyderabad",
        area="Madhapur",
        pincode="500081",
    )


def make_service_request():
    return SimpleNamespace(
        request_id=100,
        request_uuid=request_uuid,
        customer_id=1,
        skill_id=1,
        assigned_technician_id=10,
        problem_description="AC is not cooling",
        priority="High",
        status="PENDING",
        request_date=datetime.now(),
    )


def make_session_context(mock_get_session_context, session):
    """Configure get_session_context() as a context manager."""
    mock_get_session_context.return_value.__enter__.return_value = session
    mock_get_session_context.return_value.__exit__.return_value = False


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


# ============================================================
# API - VIEW ASSIGNED SERVICE REQUESTS
# ============================================================

@patch("Api.technician.get_assigned_service_requests")
def test_view_assigned_service_requests_success(mock_get):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = technician_user

    mock_get.return_value = [
        {
            "request_uuid": request_uuid,
            "service": "AC Repair",
            "problem_description": "AC is not cooling",
            "priority": "High",
            "status": "PENDING",
            "request_date": datetime.now(),
            "customer": {
                "customer_uuid": customer_uuid,
                "customer_name": "Test Customer",
                "phone": "9876543210",
                "city": "Hyderabad",
                "area": "Madhapur",
                "pincode": "500081",
            },
        }
    ]

    try:
        response = client.get("/technician/service-requests")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["service_requests"][0]["service"] == "AC Repair"


@patch("Api.technician.get_assigned_service_requests")
def test_view_assigned_service_requests_empty(mock_get):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = technician_user

    mock_get.return_value = []

    try:
        response = client.get("/technician/service-requests")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["count"] == 0
    assert response.json()["service_requests"] == []


@patch("Api.technician.get_assigned_service_requests")
def test_view_assigned_service_requests_technician_not_found(mock_get):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = technician_user

    mock_get.return_value = None

    try:
        response = client.get("/technician/service-requests")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Technician not found."


def test_view_assigned_service_requests_wrong_role():
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = customer_user

    try:
        response = client.get("/technician/service-requests")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Technician access required."


# ============================================================
# API - VIEW ONE ASSIGNED SERVICE REQUEST
# ============================================================

@patch("Api.technician.get_assigned_service_request")
def test_view_assigned_service_request_success(mock_get):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = technician_user

    mock_get.return_value = {
        "request_uuid": request_uuid,
        "service": "AC Repair",
        "problem_description": "AC is not cooling",
        "priority": "High",
        "status": "PENDING",
        "request_date": datetime.now(),
        "customer": {
            "customer_uuid": customer_uuid,
            "customer_name": "Test Customer",
            "phone": "9876543210",
            "city": "Hyderabad",
            "area": "Madhapur",
            "pincode": "500081",
        },
    }

    try:
        response = client.get(
            f"/technician/service-requests/{request_uuid}"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["service"] == "AC Repair"


@patch("Api.technician.get_assigned_service_request")
def test_view_assigned_service_request_not_found(mock_get):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = technician_user

    mock_get.return_value = None

    try:
        response = client.get(
            f"/technician/service-requests/{request_uuid}"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Assigned service request not found."


def test_view_assigned_service_request_wrong_role():
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = customer_user

    try:
        response = client.get(
            f"/technician/service-requests/{request_uuid}"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Technician access required."


# ============================================================
# SERVICE LAYER - GET ASSIGNED REQUESTS
# ============================================================

@patch("modules.technician_service.get_session_context")
def test_get_assigned_requests_technician_not_found(
    mock_get_session_context,
):
    session = MagicMock()
    make_session_context(mock_get_session_context, session)
    session.exec.return_value = first_result(None)

    result = get_assigned_service_requests(technician_uuid)

    assert result is None


@patch("modules.technician_service.get_session_context")
def test_get_assigned_requests_empty(mock_get_session_context):
    session = MagicMock()
    make_session_context(mock_get_session_context, session)

    session.exec.side_effect = [
        first_result(make_technician()),
        all_result([]),
    ]

    result = get_assigned_service_requests(technician_uuid)

    assert result == []


@patch("modules.technician_service.get_session_context")
def test_get_assigned_requests_success(mock_get_session_context):
    session = MagicMock()
    make_session_context(mock_get_session_context, session)

    session.exec.side_effect = [
        first_result(make_technician()),
        all_result([
            (
                make_service_request(),
                make_skill(),
                make_customer(),
            )
        ]),
    ]

    result = get_assigned_service_requests(technician_uuid)

    assert len(result) == 1
    assert result[0]["request_uuid"] == request_uuid
    assert result[0]["service"] == "AC Repair"
    assert result[0]["problem_description"] == "AC is not cooling"
    assert result[0]["priority"] == "High"
    assert result[0]["status"] == "PENDING"
    assert result[0]["customer"]["customer_name"] == "Test Customer"
    assert result[0]["customer"]["city"] == "Hyderabad"
    assert result[0]["customer"]["area"] == "Madhapur"
    assert result[0]["customer"]["pincode"] == "500081"


# ============================================================
# SERVICE LAYER - GET ONE ASSIGNED REQUEST
# ============================================================

@patch("modules.technician_service.get_session_context")
def test_get_assigned_request_technician_not_found(
    mock_get_session_context,
):
    session = MagicMock()
    make_session_context(mock_get_session_context, session)
    session.exec.return_value = first_result(None)

    result = get_assigned_service_request(
        technician_uuid,
        request_uuid,
    )

    assert result is None


@patch("modules.technician_service.get_session_context")
def test_get_assigned_request_not_found(mock_get_session_context):
    session = MagicMock()
    make_session_context(mock_get_session_context, session)

    session.exec.side_effect = [
        first_result(make_technician()),
        first_result(None),
    ]

    result = get_assigned_service_request(
        technician_uuid,
        request_uuid,
    )

    assert result is None


@patch("modules.technician_service.get_session_context")
def test_get_assigned_request_success(mock_get_session_context):
    session = MagicMock()
    make_session_context(mock_get_session_context, session)

    session.exec.side_effect = [
        first_result(make_technician()),
        first_result((
            make_service_request(),
            make_skill(),
            make_customer(),
        )),
    ]

    result = get_assigned_service_request(
        technician_uuid,
        request_uuid,
    )

    assert result["request_uuid"] == request_uuid
    assert result["service"] == "AC Repair"
    assert result["problem_description"] == "AC is not cooling"
    assert result["priority"] == "High"
    assert result["status"] == "PENDING"
    assert result["customer"]["customer_uuid"] == customer_uuid
    assert result["customer"]["customer_name"] == "Test Customer"
    assert result["customer"]["phone"] == "9876543210"
    assert result["customer"]["city"] == "Hyderabad"
    assert result["customer"]["area"] == "Madhapur"
    assert result["customer"]["pincode"] == "500081"


# ============================================================
# SESSION MOCK COVERAGE
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
        results=[
            "first result",
            "second result",
        ]
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
