from  datetime import datetime
from  types import SimpleNamespace
from  uuid import uuid4
from  unittest.mock import MagicMock, patch

import pytest
from  fastapi.testclient import TestClient

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

from tests.mocks.session_mock import SessionMock


client = TestClient(app)


# ============================================================
# COMMON TEST DATA
# ============================================================

request_uuid = uuid4()
customer_uuid = uuid4()
technician_uuid = uuid4()


def customer_user():
    return {
        "user_uuid": str(customer_uuid),
        "role": "customer"
    }


def technician_user():
    return {
        "user_uuid": str(technician_uuid),
        "role": "technician"
    }


def invalid_user():
    return {
        "user_uuid": str(uuid4()),
        "role": "admin"
    }


def make_service_request(
    customer_id=1,
    technician_id=10,
    status="IN PROGRESS"
):
    return SimpleNamespace(
        request_id=100,
        request_uuid=request_uuid,
        customer_id=customer_id,
        assigned_technician_id=technician_id,
        status=status
    )


def make_customer():
    return SimpleNamespace(
        customer_id=1,
        customer_uuid=customer_uuid,
        customer_name="Test Customer"
    )


def make_technician():
    return SimpleNamespace(
        technician_id=10,
        technician_uuid=technician_uuid,
        technician_name="Test Technician"
    )


def make_history_record():
    return SimpleNamespace(
        old_status="PENDING",
        new_status="IN PROGRESS",
        updated_time=datetime.now(),
        remarks="Technician started the work."
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


def all_result(value):

    result = MagicMock()

    result.first.return_value = None
    result.all.return_value = value

    return result


# ============================================================
# API - SUCCESS
# ============================================================

@patch("Api.history.get_service_history")
def test_view_service_history_success(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.return_value = {
        "request_uuid": request_uuid,
        "current_status": "IN PROGRESS",
        "count": 1,
        "history": [
            {
                "old_status": "PENDING",
                "new_status": "IN PROGRESS",
                "updated_time": datetime.now(),
                "remarks": "Technician started the work."
            }
        ]
    }

    response = client.get(
        f"/service-history/{request_uuid}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["request_uuid"] == str(request_uuid)

    assert data["count"] == 1

    assert len(data["history"]) == 1

    assert (
        data["history"][0]["old_status"]
        == "PENDING"
    )

    assert (
        data["history"][0]["new_status"]
        == "IN PROGRESS"
    )

    assert (
        data["history"][0]["remarks"]
        == "Technician started the work."
    )

    app.dependency_overrides.clear()


# ============================================================
# API - SERVICE REQUEST NOT FOUND
# ============================================================

@patch("Api.history.get_service_history")
def test_view_service_history_request_not_found(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.side_effect = ServiceRequestNotFoundError(
        "Service request not found."
    )

    response = client.get(
        f"/service-history/{request_uuid}"
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "Service request not found."
    )

    app.dependency_overrides.clear()


# ============================================================
# API - CUSTOMER NOT FOUND
# ============================================================

@patch("Api.history.get_service_history")
def test_view_service_history_customer_not_found(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.side_effect = CustomerNotFoundError(
        "Customer not found."
    )

    response = client.get(
        f"/service-history/{request_uuid}"
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "Customer not found."
    )

    app.dependency_overrides.clear()


# ============================================================
# API - TECHNICIAN NOT FOUND
# ============================================================

@patch("Api.history.get_service_history")
def test_view_service_history_technician_not_found(mock_get):

    app.dependency_overrides[get_current_user] = technician_user

    mock_get.side_effect = TechnicianNotFoundError(
        "Technician not found."
    )

    response = client.get(
        f"/service-history/{request_uuid}"
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "Technician not found."
    )

    app.dependency_overrides.clear()


# ============================================================
# API - UNAUTHORIZED
# ============================================================

@patch("Api.history.get_service_history")
def test_view_service_history_unauthorized(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.side_effect = UnauthorizedServiceHistoryError(
        "You are not allowed to view this service history."
    )

    response = client.get(
        f"/service-history/{request_uuid}"
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "You are not allowed to view "
        "this service history."
    )

    app.dependency_overrides.clear()


# ============================================================
# API - INVALID ROLE
# ============================================================

@patch("Api.history.get_service_history")
def test_view_service_history_invalid_role(mock_get):

    app.dependency_overrides[get_current_user] = invalid_user

    mock_get.side_effect = InvalidUserRoleError(
        "Invalid user role."
    )

    response = client.get(
        f"/service-history/{request_uuid}"
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "Invalid user role."
    )

    app.dependency_overrides.clear()


# ============================================================
# SERVICE LAYER - REQUEST NOT FOUND
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_request_not_found(mock_get_session):

    session = make_session()

    session.exec.return_value = first_result(None)

    mock_get_session.return_value = session

    with pytest.raises(ServiceRequestNotFoundError):

        get_service_history(
            request_uuid,
            customer_uuid,
            "customer"
        )


# ============================================================
# SERVICE LAYER - CUSTOMER NOT FOUND
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_customer_not_found(mock_get_session):

    session = make_session()

    session.exec.side_effect = [
        first_result(
            make_service_request()
        ),
        first_result(None)
    ]

    mock_get_session.return_value = session

    with pytest.raises(CustomerNotFoundError):

        get_service_history(
            request_uuid,
            customer_uuid,
            "customer"
        )


# ============================================================
# SERVICE LAYER - CUSTOMER UNAUTHORIZED
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_customer_unauthorized(
    mock_get_session
):

    different_customer = SimpleNamespace(
        customer_id=999,
        customer_uuid=uuid4()
    )

    session = make_session()

    session.exec.side_effect = [
        first_result(
            make_service_request(
                customer_id=1
            )
        ),
        first_result(
            different_customer
        )
    ]

    mock_get_session.return_value = session

    with pytest.raises(
        UnauthorizedServiceHistoryError
    ):

        get_service_history(
            request_uuid,
            customer_uuid,
            "customer"
        )


# ============================================================
# SERVICE LAYER - CUSTOMER NO HISTORY
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_customer_no_history(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(
            make_service_request(
                customer_id=1
            )
        ),
        first_result(
            make_customer()
        ),
        all_result([])
    ]

    mock_get_session.return_value = session

    result = get_service_history(
        request_uuid,
        customer_uuid,
        "customer"
    )

    assert result["request_uuid"] == request_uuid

    assert (
        result["message"]
        == "No service history found."
    )

    assert result["history"] == []


# ============================================================
# SERVICE LAYER - CUSTOMER WITH HISTORY
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_customer_success(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(
            make_service_request(
                customer_id=1,
                status="IN PROGRESS"
            )
        ),
        first_result(
            make_customer()
        ),
        all_result([
            make_history_record()
        ])
    ]

    mock_get_session.return_value = session

    result = get_service_history(
        request_uuid,
        customer_uuid,
        "customer"
    )

    assert result["request_uuid"] == request_uuid

    assert (
        result["current_status"]
        == "IN PROGRESS"
    )

    assert result["history_count"] == 1

    assert (
        result["history"][0]["old_status"]
        == "PENDING"
    )

    assert (
        result["history"][0]["new_status"]
        == "IN PROGRESS"
    )

    assert (
        result["history"][0]["remarks"]
        == "Technician started the work."
    )


# ============================================================
# SERVICE LAYER - TECHNICIAN NOT FOUND
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_technician_not_found(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(
            make_service_request(
                technician_id=10
            )
        ),
        first_result(None)
    ]

    mock_get_session.return_value = session

    with pytest.raises(TechnicianNotFoundError):

        get_service_history(
            request_uuid,
            technician_uuid,
            "technician"
        )


# ============================================================
# SERVICE LAYER - TECHNICIAN UNAUTHORIZED
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_technician_unauthorized(
    mock_get_session
):

    different_technician = SimpleNamespace(
        technician_id=999,
        technician_uuid=uuid4()
    )

    session = make_session()

    session.exec.side_effect = [
        first_result(
            make_service_request(
                technician_id=10
            )
        ),
        first_result(
            different_technician
        )
    ]

    mock_get_session.return_value = session

    with pytest.raises(
        UnauthorizedServiceHistoryError
    ):

        get_service_history(
            request_uuid,
            technician_uuid,
            "technician"
        )


# ============================================================
# SERVICE LAYER - TECHNICIAN NO HISTORY
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_technician_no_history(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(
            make_service_request(
                technician_id=10
            )
        ),
        first_result(
            make_technician()
        ),
        all_result([])
    ]

    mock_get_session.return_value = session

    result = get_service_history(
        request_uuid,
        technician_uuid,
        "technician"
    )

    assert result["request_uuid"] == request_uuid

    assert (
        result["message"]
        == "No service history found."
    )

    assert result["history"] == []


# ============================================================
# SERVICE LAYER - TECHNICIAN WITH HISTORY
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_technician_success(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(
            make_service_request(
                technician_id=10,
                status="COMPLETED"
            )
        ),
        first_result(
            make_technician()
        ),
        all_result([
            make_history_record()
        ])
    ]

    mock_get_session.return_value = session

    result = get_service_history(
        request_uuid,
        technician_uuid,
        "technician"
    )

    assert result["request_uuid"] == request_uuid

    assert (
        result["current_status"]
        == "COMPLETED"
    )

    assert result["history_count"] == 1

    assert (
        result["history"][0]["new_status"]
        == "IN PROGRESS"
    )


# ============================================================
# SERVICE LAYER - INVALID ROLE
# ============================================================

@patch("modules.history_service.get_session")
def test_get_history_invalid_role(
    mock_get_session
):

    session = make_session()

    session.exec.return_value = first_result(
        make_service_request()
    )

    mock_get_session.return_value = session

    with pytest.raises(InvalidUserRoleError):

        get_service_history(
            request_uuid,
            uuid4(),
            "admin"
        )


# ============================================================
# SESSION MOCK COVERAGE
# ============================================================

def test_result_mock_all_with_data():

    session = SessionMock(
        result=[
            "row1",
            "row2"
        ]
    )

    result = session.exec("query")

    assert result.all() == [
        "row1",
        "row2"
    ]


def test_session_mock_get():

    expected = object()

    session = SessionMock(
        get_result=expected
    )

    assert session.get(
        "Model",
        1
    ) is expected


def test_session_mock_results_mode():

    session = SessionMock(
        results=[
            "first result",
            "second result"
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