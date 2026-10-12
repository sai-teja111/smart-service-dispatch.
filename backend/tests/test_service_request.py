from  datetime import datetime
from  types import SimpleNamespace
from  uuid import uuid4
from  unittest.mock import MagicMock, patch

import pytest
from  fastapi.testclient import TestClient

from main import app
from Api.dependencies import get_current_user

from modules.service_request_service import (
    create_service_request,
    get_customer_service_requests,
    get_customer_service_request,
    get_service_request_history,
    update_service_request_status,
    CustomerNotFoundError,
    TechnicianNotFoundError,
    ServiceRequestNotFoundError,
    UnauthorizedServiceRequestError,
    DuplicateServiceRequestError,
    InvalidServiceRequestStatusError,
)

from tests.mocks.session_mock import SessionMock


client = TestClient(app)


# ============================================================
# COMMON TEST DATA
# ============================================================

customer_uuid = uuid4()
technician_uuid = uuid4()
request_uuid = uuid4()
skill_uuid = uuid4()


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


def request_data():
    return {
        "message": "Service request created successfully.",
        "request_uuid": request_uuid,
        "service": "AC Repair",
        "problem_description": "AC is not cooling",
        "priority": "High",
        "status": "OPEN",
        "request_date": datetime.now(),
        "technician": None
    }


def make_customer():
    return SimpleNamespace(
        customer_id=1,
        customer_uuid=customer_uuid
    )


def make_skill():
    return SimpleNamespace(
        skill_id=1,
        skill_uuid=skill_uuid,
        skill_name="AC Repair"
    )


def make_technician(
    workload=2,
    availability="Available"
):
    return SimpleNamespace(
        technician_id=10,
        technician_uuid=technician_uuid,
        technician_name="Test Technician",
        workload=workload,
        availability=availability
    )


def make_service_request(
    status="PENDING",
    technician_id=10
):
    return SimpleNamespace(
        request_id=100,
        request_uuid=request_uuid,
        customer_id=1,
        skill_id=1,
        problem_description="AC is not cooling",
        priority="High",
        status=status,
        assigned_technician_id=technician_id,
        request_date=datetime.now()
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
# API - CREATE SERVICE REQUEST
# ============================================================

@patch("Api.service_request.create_service_request_service")
def test_create_service_request_success(mock_create):

    app.dependency_overrides[get_current_user] = customer_user

    mock_create.return_value = request_data()

    response = client.post(
        "/service-requests",
        json={
            "problem_description": "AC is not cooling",
            "skill_id": 1,
            "priority": "High"
        }
    )

    assert response.status_code == 200
    assert response.json()["service"] == "AC Repair"

    app.dependency_overrides.clear()


@patch("Api.service_request.create_service_request_service")
def test_create_service_request_customer_not_found(mock_create):

    app.dependency_overrides[get_current_user] = customer_user

    mock_create.side_effect = CustomerNotFoundError(
        "Customer not found."
    )

    response = client.post(
        "/service-requests",
        json={
            "problem_description": "AC problem",
            "skill_id": 1,
            "priority": "High"
        }
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


@patch("Api.service_request.create_service_request_service")
def test_create_service_request_duplicate(mock_create):

    app.dependency_overrides[get_current_user] = customer_user

    mock_create.side_effect = DuplicateServiceRequestError(
        "Duplicate service request."
    )

    response = client.post(
        "/service-requests",
        json={
            "problem_description": "AC problem",
            "skill_id": 1,
            "priority": "High"
        }
    )

    assert response.status_code == 409

    app.dependency_overrides.clear()


@patch("Api.service_request.create_service_request_service")
def test_create_service_request_invalid(mock_create):

    app.dependency_overrides[get_current_user] = customer_user

    mock_create.side_effect = ValueError(
        "Invalid service request data."
    )

    response = client.post(
        "/service-requests",
        json={
            "problem_description": "AC problem",
            "skill_id": 1,
            "priority": "High"
        }
    )

    assert response.status_code == 400

    app.dependency_overrides.clear()


def test_create_service_request_wrong_role():

    app.dependency_overrides[get_current_user] = technician_user

    response = client.post(
        "/service-requests",
        json={
            "problem_description": "AC problem",
            "skill_id": 1,
            "priority": "High"
        }
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()


# ============================================================
# API - VIEW SERVICE REQUESTS
# ============================================================

@patch("Api.service_request.get_customer_service_requests")
def test_view_service_requests_success(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.return_value = [request_data()]

    response = client.get("/service-requests")

    assert response.status_code == 200
    assert response.json()["count"] == 1

    app.dependency_overrides.clear()


@patch("Api.service_request.get_customer_service_requests")
def test_view_service_requests_empty(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.return_value = []

    response = client.get("/service-requests")

    assert response.status_code == 200
    assert response.json()["count"] == 0

    app.dependency_overrides.clear()


@patch("Api.service_request.get_customer_service_requests")
def test_view_service_requests_customer_not_found(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.side_effect = CustomerNotFoundError(
        "Customer not found."
    )

    response = client.get("/service-requests")

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_view_service_requests_wrong_role():

    app.dependency_overrides[get_current_user] = technician_user

    response = client.get("/service-requests")

    assert response.status_code == 403

    app.dependency_overrides.clear()


# ============================================================
# API - VIEW SERVICE REQUEST HISTORY
# ============================================================

@patch("Api.service_request.get_service_request_history")
def test_view_history_success(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.return_value = {
        "request_uuid": request_uuid,
        "count": 0,
        "history": []
    }

    response = client.get(
        f"/service-requests/{request_uuid}/history"
    )

    assert response.status_code == 200

    app.dependency_overrides.clear()


@patch("Api.service_request.get_service_request_history")
def test_view_history_customer_not_found(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.side_effect = CustomerNotFoundError(
        "Customer not found."
    )

    response = client.get(
        f"/service-requests/{request_uuid}/history"
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


@patch("Api.service_request.get_service_request_history")
def test_view_history_request_not_found(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.side_effect = ServiceRequestNotFoundError(
        "Service request not found."
    )

    response = client.get(
        f"/service-requests/{request_uuid}/history"
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_view_history_wrong_role():

    app.dependency_overrides[get_current_user] = technician_user

    response = client.get(
        f"/service-requests/{request_uuid}/history"
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()


# ============================================================
# API - VIEW ONE SERVICE REQUEST
# ============================================================

@patch("Api.service_request.get_customer_service_request")
def test_view_request_success(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.return_value = request_data()

    response = client.get(
        f"/service-requests/{request_uuid}"
    )

    assert response.status_code == 200

    app.dependency_overrides.clear()


@patch("Api.service_request.get_customer_service_request")
def test_view_request_customer_not_found(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.side_effect = CustomerNotFoundError(
        "Customer not found."
    )

    response = client.get(
        f"/service-requests/{request_uuid}"
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


@patch("Api.service_request.get_customer_service_request")
def test_view_request_not_found(mock_get):

    app.dependency_overrides[get_current_user] = customer_user

    mock_get.side_effect = ServiceRequestNotFoundError(
        "Service request not found."
    )

    response = client.get(
        f"/service-requests/{request_uuid}"
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_view_request_wrong_role():

    app.dependency_overrides[get_current_user] = technician_user

    response = client.get(
        f"/service-requests/{request_uuid}"
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()


# ============================================================
# API - UPDATE SERVICE REQUEST STATUS
# ============================================================

@patch("Api.service_request.update_service_request_status_service")
def test_update_status_success(mock_update):

    app.dependency_overrides[get_current_user] = technician_user

    mock_update.return_value = {
        "message": "Service request status updated successfully.",
        "request_uuid": request_uuid,
        "old_status": "PENDING",
        "new_status": "IN PROGRESS",
        "remarks": "Started work",
        "technician": {
            "technician_uuid": technician_uuid,
            "technician_name": "Test Technician",
            "previous_workload": 2,
            "new_workload": 2,
            "availability": "Available",
            "availability_changed": False
        }
    }

    response = client.patch(
        f"/service-requests/{request_uuid}/status",
        json={
            "status": "IN_PROGRESS",
            "remarks": "Started work"
        }
    )

    assert response.status_code == 200

    app.dependency_overrides.clear()


@patch("Api.service_request.update_service_request_status_service")
def test_update_status_technician_not_found(mock_update):

    app.dependency_overrides[get_current_user] = technician_user

    mock_update.side_effect = TechnicianNotFoundError(
        "Technician not found."
    )

    response = client.patch(
        f"/service-requests/{request_uuid}/status",
        json={
            "status": "IN_PROGRESS"
        }
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


@patch("Api.service_request.update_service_request_status_service")
def test_update_status_request_not_found(mock_update):

    app.dependency_overrides[get_current_user] = technician_user

    mock_update.side_effect = ServiceRequestNotFoundError(
        "Service request not found."
    )

    response = client.patch(
        f"/service-requests/{request_uuid}/status",
        json={
            "status": "IN_PROGRESS"
        }
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


@patch("Api.service_request.update_service_request_status_service")
def test_update_status_unauthorized(mock_update):

    app.dependency_overrides[get_current_user] = technician_user

    mock_update.side_effect = UnauthorizedServiceRequestError(
        "You are not assigned to this service request."
    )

    response = client.patch(
        f"/service-requests/{request_uuid}/status",
        json={
            "status": "IN_PROGRESS"
        }
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()


@patch("Api.service_request.update_service_request_status_service")
def test_update_status_invalid(mock_update):

    app.dependency_overrides[get_current_user] = technician_user

    mock_update.side_effect = InvalidServiceRequestStatusError(
        "Invalid status."
    )

    response = client.patch(
        f"/service-requests/{request_uuid}/status",
        json={
            "status": "COMPLETED"
        }
    )

    assert response.status_code == 400

    app.dependency_overrides.clear()


def test_update_status_wrong_role():

    app.dependency_overrides[get_current_user] = customer_user

    response = client.patch(
        f"/service-requests/{request_uuid}/status",
        json={
            "status": "COMPLETED"
        }
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()


# ============================================================
# SERVICE LAYER - CREATE REQUEST
# ============================================================

@patch("modules.service_request_service.get_session")
def test_create_customer_not_found(mock_get_session):

    session = make_session()

    session.exec.return_value = first_result(None)

    mock_get_session.return_value = session

    with pytest.raises(CustomerNotFoundError):

        create_service_request(
            customer_uuid,
            "AC is not cooling",
            1,
            "High"
        )


@patch("modules.service_request_service.get_session")
def test_create_invalid_priority(mock_get_session):

    session = make_session()

    session.exec.return_value = first_result(
        make_customer()
    )

    mock_get_session.return_value = session

    with pytest.raises(ValueError):

        create_service_request(
            customer_uuid,
            "AC is not cooling",
            1,
            "Urgent"
        )


@patch(
    "modules.service_request_service.find_service_by_problem"
)
@patch("modules.service_request_service.get_session")
def test_create_service_not_identified(
    mock_get_session,
    mock_find_service
):

    session = make_session()

    session.exec.return_value = first_result(
        make_customer()
    )

    mock_get_session.return_value = session

    mock_find_service.return_value = None

    with pytest.raises(ValueError):

        create_service_request(
            customer_uuid,
            "Unknown problem",
            None,
            "High"
        )


@patch("modules.service_request_service.get_session")
def test_create_skill_not_found(mock_get_session):

    session = make_session()

    session.exec.return_value = first_result(
        make_customer()
    )

    session.get.return_value = None

    mock_get_session.return_value = session

    with pytest.raises(ValueError):

        create_service_request(
            customer_uuid,
            "AC is not cooling",
            999,
            "High"
        )


@patch(
    "modules.service_request_service.has_pending_service_request"
)
@patch("modules.service_request_service.get_session")
def test_create_duplicate_request(
    mock_get_session,
    mock_pending
):

    session = make_session()

    session.exec.return_value = first_result(
        make_customer()
    )

    session.get.return_value = make_skill()

    mock_get_session.return_value = session

    mock_pending.return_value = True

    with pytest.raises(DuplicateServiceRequestError):

        create_service_request(
            customer_uuid,
            "AC is not cooling",
            1,
            "High"
        )


@patch(
    "modules.service_request_service.find_best_technician"
)
@patch(
    "modules.service_request_service.has_pending_service_request"
)
@patch("modules.service_request_service.get_session")
def test_create_without_technician(
    mock_get_session,
    mock_pending,
    mock_find_best
):

    session = make_session()

    session.exec.return_value = first_result(
        make_customer()
    )

    session.get.side_effect = [
        make_skill(),
        make_service_request(status="OPEN")
    ]

    mock_get_session.return_value = session

    mock_pending.return_value = False
    mock_find_best.return_value = None

    result = create_service_request(
        customer_uuid,
        "AC is not cooling",
        1,
        "High"
    )

    assert result["service"] == "AC Repair"
    assert result["status"] == "OPEN"
    assert result["priority"] == "High"
    assert result["technician"] is None

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()


@patch(
    "modules.service_request_service.find_best_technician"
)
@patch(
    "modules.service_request_service.has_pending_service_request"
)
@patch("modules.service_request_service.get_session")
def test_create_with_technician(
    mock_get_session,
    mock_pending,
    mock_find_best
):

    session = make_session()

    session.exec.return_value = first_result(
        make_customer()
    )

    session.get.side_effect = [
        make_skill(),
        make_technician(),
        make_service_request(status="OPEN")
    ]

    mock_get_session.return_value = session

    mock_pending.return_value = False
    mock_find_best.return_value = 10

    result = create_service_request(
        customer_uuid,
        "AC is not cooling",
        1,
        "High"
    )

    assert result["technician"] is not None

    assert (
        result["technician"]["technician_name"]
        == "Test Technician"
    )


@patch(
    "modules.service_request_service.find_best_technician"
)
@patch(
    "modules.service_request_service.has_pending_service_request"
)
@patch("modules.service_request_service.get_session")
def test_create_technician_not_found(
    mock_get_session,
    mock_pending,
    mock_find_best
):

    session = make_session()

    session.exec.return_value = first_result(
        make_customer()
    )

    session.get.side_effect = [
        make_skill(),
        None,
        make_service_request(status="OPEN")
    ]

    mock_get_session.return_value = session

    mock_pending.return_value = False
    mock_find_best.return_value = 10

    result = create_service_request(
        customer_uuid,
        "AC is not cooling",
        1,
        "High"
    )

    assert result["technician"] is None


@patch(
    "modules.service_request_service.find_best_technician"
)
@patch(
    "modules.service_request_service.has_pending_service_request"
)
@patch("modules.service_request_service.get_session")
def test_create_updated_request_not_found(
    mock_get_session,
    mock_pending,
    mock_find_best
):

    session = make_session()

    session.exec.return_value = first_result(
        make_customer()
    )

    session.get.side_effect = [
        make_skill(),
        None
    ]

    mock_get_session.return_value = session

    mock_pending.return_value = False
    mock_find_best.return_value = None

    with pytest.raises(ServiceRequestNotFoundError):

        create_service_request(
            customer_uuid,
            "AC is not cooling",
            1,
            "High"
        )


@patch(
    "modules.service_request_service.find_service_by_problem"
)
@patch(
    "modules.service_request_service.find_best_technician"
)
@patch(
    "modules.service_request_service.has_pending_service_request"
)
@patch("modules.service_request_service.get_session")
def test_create_semantic_detection(
    mock_get_session,
    mock_pending,
    mock_find_best,
    mock_find_service
):

    session = make_session()

    session.exec.return_value = first_result(
        make_customer()
    )

    session.get.side_effect = [
        make_skill(),
        make_service_request(status="OPEN")
    ]

    mock_get_session.return_value = session

    mock_find_service.return_value = {
        "skill_id": 1,
        "match_type": "semantic",
        "distance": 0.15
    }

    mock_pending.return_value = False
    mock_find_best.return_value = None

    result = create_service_request(
        customer_uuid,
        "AC is not cooling",
        None,
        "High"
    )

    assert "service_detection" in result

    assert (
        result["service_detection"]["match_type"]
        == "semantic"
    )

    assert (
        result["service_detection"]["distance"]
        == 0.15
    )


# ============================================================
# SERVICE LAYER - GET CUSTOMER REQUESTS
# ============================================================

@patch("modules.service_request_service.get_session")
def test_get_customer_requests_not_found(
    mock_get_session
):

    session = make_session()

    session.exec.return_value = first_result(None)

    mock_get_session.return_value = session

    with pytest.raises(CustomerNotFoundError):

        get_customer_service_requests(
            customer_uuid
        )


@patch("modules.service_request_service.get_session")
def test_get_customer_requests_empty(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_customer()),
        all_result([])
    ]

    mock_get_session.return_value = session

    result = get_customer_service_requests(
        customer_uuid
    )

    assert result == []


@patch("modules.service_request_service.get_session")
def test_get_customer_requests_with_technician(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_customer()),
        all_result([
            (
                make_service_request(),
                make_skill(),
                make_technician()
            )
        ])
    ]

    mock_get_session.return_value = session

    result = get_customer_service_requests(
        customer_uuid
    )

    assert len(result) == 1

    assert result[0]["service"] == "AC Repair"

    assert (
        result[0]["technician"]["technician_name"]
        == "Test Technician"
    )


@patch("modules.service_request_service.get_session")
def test_get_customer_requests_without_technician(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_customer()),
        all_result([
            (
                make_service_request(
                    technician_id=None
                ),
                make_skill(),
                None
            )
        ])
    ]

    mock_get_session.return_value = session

    result = get_customer_service_requests(
        customer_uuid
    )

    assert result[0]["technician"] is None


# ============================================================
# SERVICE LAYER - GET ONE REQUEST
# ============================================================

@patch("modules.service_request_service.get_session")
def test_get_one_customer_not_found(
    mock_get_session
):

    session = make_session()

    session.exec.return_value = first_result(None)

    mock_get_session.return_value = session

    with pytest.raises(CustomerNotFoundError):

        get_customer_service_request(
            customer_uuid,
            request_uuid
        )


@patch("modules.service_request_service.get_session")
def test_get_one_request_not_found(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(None)
    ]

    mock_get_session.return_value = session

    with pytest.raises(ServiceRequestNotFoundError):

        get_customer_service_request(
            customer_uuid,
            request_uuid
        )


@patch("modules.service_request_service.get_session")
def test_get_one_request_with_technician(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result((
            make_service_request(),
            make_skill(),
            make_technician()
        ))
    ]

    mock_get_session.return_value = session

    result = get_customer_service_request(
        customer_uuid,
        request_uuid
    )

    assert result["service"] == "AC Repair"

    assert (
        result["technician"]["technician_name"]
        == "Test Technician"
    )


@patch("modules.service_request_service.get_session")
def test_get_one_request_without_technician(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result((
            make_service_request(
                technician_id=None
            ),
            make_skill(),
            None
        ))
    ]

    mock_get_session.return_value = session

    result = get_customer_service_request(
        customer_uuid,
        request_uuid
    )

    assert result["technician"] is None


# ============================================================
# SERVICE LAYER - HISTORY
# ============================================================

@patch("modules.service_request_service.get_session")
def test_history_customer_not_found(
    mock_get_session
):

    session = make_session()

    session.exec.return_value = first_result(None)

    mock_get_session.return_value = session

    with pytest.raises(CustomerNotFoundError):

        get_service_request_history(
            customer_uuid,
            request_uuid
        )


@patch("modules.service_request_service.get_session")
def test_history_request_not_found(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(None)
    ]

    mock_get_session.return_value = session

    with pytest.raises(ServiceRequestNotFoundError):

        get_service_request_history(
            customer_uuid,
            request_uuid
        )


@patch("modules.service_request_service.get_session")
def test_history_empty(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(make_service_request()),
        all_result([])
    ]

    mock_get_session.return_value = session

    result = get_service_request_history(
        customer_uuid,
        request_uuid
    )

    assert result["count"] == 0
    assert result["history"] == []


@patch("modules.service_request_service.get_session")
def test_history_with_records(
    mock_get_session
):

    session = make_session()

    history = SimpleNamespace(
        old_status="PENDING",
        new_status="IN PROGRESS",
        remarks="Started work",
        updated_time=datetime.now()
    )

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(make_service_request()),
        all_result([history])
    ]

    mock_get_session.return_value = session

    result = get_service_request_history(
        customer_uuid,
        request_uuid
    )

    assert result["count"] == 1

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
        == "Started work"
    )


# ============================================================
# SERVICE LAYER - UPDATE STATUS
# ============================================================

@patch("modules.service_request_service.get_session")
def test_update_invalid_status(mock_get_session):

    with pytest.raises(
        InvalidServiceRequestStatusError
    ):

        update_service_request_status(
            technician_uuid,
            request_uuid,
            "OPEN",
            None
        )

    mock_get_session.assert_not_called()


@patch("modules.service_request_service.get_session")
def test_update_technician_not_found(
    mock_get_session
):

    session = make_session()

    session.exec.return_value = first_result(None)

    mock_get_session.return_value = session

    with pytest.raises(TechnicianNotFoundError):

        update_service_request_status(
            technician_uuid,
            request_uuid,
            "IN_PROGRESS",
            None
        )


@patch("modules.service_request_service.get_session")
def test_update_request_not_found(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_technician()),
        first_result(None)
    ]

    mock_get_session.return_value = session

    with pytest.raises(ServiceRequestNotFoundError):

        update_service_request_status(
            technician_uuid,
            request_uuid,
            "IN_PROGRESS",
            None
        )


@patch("modules.service_request_service.get_session")
def test_update_unauthorized(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_technician()),
        first_result(
            make_service_request(
                technician_id=999
            )
        )
    ]

    mock_get_session.return_value = session

    with pytest.raises(
        UnauthorizedServiceRequestError
    ):

        update_service_request_status(
            technician_uuid,
            request_uuid,
            "IN_PROGRESS",
            None
        )


@patch("modules.service_request_service.get_session")
def test_update_same_status(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_technician()),
        first_result(
            make_service_request(
                status="IN PROGRESS"
            )
        )
    ]

    mock_get_session.return_value = session

    with pytest.raises(
        InvalidServiceRequestStatusError
    ):

        update_service_request_status(
            technician_uuid,
            request_uuid,
            "IN_PROGRESS",
            None
        )


@patch("modules.service_request_service.get_session")
def test_update_invalid_progress_transition(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_technician()),
        first_result(
            make_service_request(
                status="OPEN"
            )
        )
    ]

    mock_get_session.return_value = session

    with pytest.raises(
        InvalidServiceRequestStatusError
    ):

        update_service_request_status(
            technician_uuid,
            request_uuid,
            "IN_PROGRESS",
            None
        )


@patch("modules.service_request_service.get_session")
def test_update_invalid_completed_transition(
    mock_get_session
):

    session = make_session()

    session.exec.side_effect = [
        first_result(make_technician()),
        first_result(
            make_service_request(
                status="PENDING"
            )
        )
    ]

    mock_get_session.return_value = session

    with pytest.raises(
        InvalidServiceRequestStatusError
    ):

        update_service_request_status(
            technician_uuid,
            request_uuid,
            "COMPLETED",
            None
        )


@patch("modules.service_request_service.get_session")
def test_update_in_progress(
    mock_get_session
):

    technician = make_technician()

    request = make_service_request(
        status="PENDING"
    )

    session = make_session()

    session.exec.side_effect = [
        first_result(technician),
        first_result(request)
    ]

    mock_get_session.return_value = session

    result = update_service_request_status(
        technician_uuid,
        request_uuid,
        "IN_PROGRESS",
        "Started work"
    )

    assert result["old_status"] == "PENDING"
    assert result["new_status"] == "IN PROGRESS"
    assert result["remarks"] == "Started work"

    assert technician.workload == 2

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()


@patch("modules.service_request_service.get_session")
def test_update_in_progress_with_space(
    mock_get_session
):

    technician = make_technician()

    request = make_service_request(
        status="PENDING"
    )

    session = make_session()

    session.exec.side_effect = [
        first_result(technician),
        first_result(request)
    ]

    mock_get_session.return_value = session

    result = update_service_request_status(
        technician_uuid,
        request_uuid,
        "IN PROGRESS",
        None
    )

    assert result["new_status"] == "IN PROGRESS"
    assert result["remarks"] is None


@patch("modules.service_request_service.get_session")
def test_update_completed_busy(
    mock_get_session
):

    technician = make_technician(
        workload=5,
        availability="Busy"
    )

    request = make_service_request(
        status="IN PROGRESS"
    )

    session = make_session()

    session.exec.side_effect = [
        first_result(technician),
        first_result(request)
    ]

    mock_get_session.return_value = session

    result = update_service_request_status(
        technician_uuid,
        request_uuid,
        "COMPLETED",
        "Completed successfully"
    )

    assert result["old_status"] == "IN PROGRESS"
    assert result["new_status"] == "COMPLETED"
    assert result["remarks"] == "Completed successfully"

    assert (
        result["technician"]["previous_workload"]
        == 5
    )

    assert (
        result["technician"]["new_workload"]
        == 4
    )

    assert (
        result["technician"]["availability"]
        == "Available"
    )

    assert (
        result["technician"]["availability_changed"]
        is True
    )


@patch("modules.service_request_service.get_session")
def test_update_completed_no_availability_change(
    mock_get_session
):

    technician = make_technician(
        workload=0,
        availability="Unavailable"
    )

    request = make_service_request(
        status="IN PROGRESS"
    )

    session = make_session()

    session.exec.side_effect = [
        first_result(technician),
        first_result(request)
    ]

    mock_get_session.return_value = session

    result = update_service_request_status(
        technician_uuid,
        request_uuid,
        "COMPLETED",
        None
    )

    assert result["new_status"] == "COMPLETED"

    assert (
        result["technician"]["new_workload"]
        == 0
    )

    assert (
        result["technician"]["availability_changed"]
        is False
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