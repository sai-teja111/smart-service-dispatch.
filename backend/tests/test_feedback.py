from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from Api.dependencies import get_current_user

from modules.feedback_service import (
    create_feedback,
    get_feedback,
    CustomerNotFoundError,
    ServiceRequestNotFoundError,
    UnauthorizedFeedbackError,
    IncompleteServiceError,
    NoTechnicianAssignedError,
    FeedbackAlreadyExistsError,
    TechnicianNotFoundError,
    InvalidUserRoleError,
)

from tests.mocks.session_mock import SessionMock


client = TestClient(app)


# ============================================================
# COMMON TEST DATA
# ============================================================

customer_uuid = uuid4()
technician_uuid = uuid4()
request_uuid = uuid4()
feedback_uuid = uuid4()


def customer_user():
    return {
        "user_uuid": str(customer_uuid),
        "role": "customer",
    }


def technician_user():
    return {
        "user_uuid": str(technician_uuid),
        "role": "technician",
    }


def invalid_user():
    return {
        "user_uuid": str(uuid4()),
        "role": "admin",
    }


def make_customer():
    return SimpleNamespace(
        customer_id=1,
        customer_uuid=customer_uuid,
        customer_name="Test Customer",
    )


def make_technician(technician_id=10, rating=4.5):
    return SimpleNamespace(
        technician_id=technician_id,
        technician_uuid=technician_uuid,
        technician_name="Test Technician",
        rating=rating,
    )


def make_service_request(
    customer_id=1,
    technician_id=10,
    status="COMPLETED",
):
    return SimpleNamespace(
        request_id=100,
        request_uuid=request_uuid,
        customer_id=customer_id,
        assigned_technician_id=technician_id,
        status=status,
    )


def make_feedback(rating=4.5, comments="Good service"):
    return SimpleNamespace(
        feedback_id=500,
        feedback_uuid=feedback_uuid,
        request_id=100,
        customer_id=1,
        technician_id=10,
        rating=rating,
        comments=comments,
        feedback_date=datetime.now(),
    )


def make_session():
    """Create a mocked session suitable for get_session_context()."""
    session = MagicMock()
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


def configure_session_context(mock_context, session):
    """Make the mocked context manager yield the supplied session."""
    mock_context.return_value.__enter__.return_value = session
    mock_context.return_value.__exit__.return_value = False


# ============================================================
# API - CREATE FEEDBACK SUCCESS
# ============================================================

@patch("Api.feedback.create_feedback_service")
def test_create_feedback_success(mock_create):
    app.dependency_overrides[get_current_user] = customer_user

    mock_create.return_value = {
        "message": "Feedback submitted successfully.",
        "feedback_uuid": feedback_uuid,
        "request_uuid": request_uuid,
        "rating": 4.5,
        "comments": "Good service",
        "technician": {
            "technician_uuid": technician_uuid,
            "technician_name": "Test Technician",
            "rating": 4.5,
        },
    }

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 4.5,
                "comments": "Good service",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Feedback submitted successfully."
        assert data["feedback_uuid"] == str(feedback_uuid)
        assert data["request_uuid"] == str(request_uuid)
        assert data["rating"] == "4.5"
        assert data["comments"] == "Good service"
        assert data["technician"]["technician_name"] == "Test Technician"
        assert data["technician"]["rating"] == "4.5"
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - CREATE FEEDBACK WRONG ROLE
# ============================================================

def test_create_feedback_wrong_role():
    app.dependency_overrides[get_current_user] = technician_user

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 4,
                "comments": "Good",
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == (
            "Customer access required."
        )
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - CREATE FEEDBACK CUSTOMER NOT FOUND
# ============================================================

@patch("Api.feedback.create_feedback_service")
def test_create_feedback_customer_not_found(mock_create):
    app.dependency_overrides[get_current_user] = customer_user
    mock_create.side_effect = CustomerNotFoundError("Customer not found.")

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 4,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Customer not found."
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - CREATE FEEDBACK REQUEST NOT FOUND
# ============================================================

@patch("Api.feedback.create_feedback_service")
def test_create_feedback_request_not_found(mock_create):
    app.dependency_overrides[get_current_user] = customer_user
    mock_create.side_effect = ServiceRequestNotFoundError(
        "Service request not found."
    )

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 4,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Service request not found."
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - CREATE FEEDBACK UNAUTHORIZED
# ============================================================

@patch("Api.feedback.create_feedback_service")
def test_create_feedback_unauthorized(mock_create):
    app.dependency_overrides[get_current_user] = customer_user
    mock_create.side_effect = UnauthorizedFeedbackError(
        "You are not allowed to give feedback "
        "for this service request."
    )

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 4,
            },
        )

        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - CREATE FEEDBACK INCOMPLETE SERVICE
# ============================================================

@patch("Api.feedback.create_feedback_service")
def test_create_feedback_incomplete(mock_create):
    app.dependency_overrides[get_current_user] = customer_user
    mock_create.side_effect = IncompleteServiceError(
        "Feedback can only be submitted "
        "after the service is completed."
    )

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 4,
            },
        )

        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - CREATE FEEDBACK NO TECHNICIAN
# ============================================================

@patch("Api.feedback.create_feedback_service")
def test_create_feedback_no_technician(mock_create):
    app.dependency_overrides[get_current_user] = customer_user
    mock_create.side_effect = NoTechnicianAssignedError(
        "No technician is assigned to this request."
    )

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 4,
            },
        )

        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - CREATE FEEDBACK DUPLICATE
# ============================================================

@patch("Api.feedback.create_feedback_service")
def test_create_feedback_duplicate(mock_create):
    app.dependency_overrides[get_current_user] = customer_user
    mock_create.side_effect = FeedbackAlreadyExistsError(
        "Feedback has already been submitted."
    )

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 4,
            },
        )

        assert response.status_code == 409
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - CREATE FEEDBACK TECHNICIAN NOT FOUND
# ============================================================

@patch("Api.feedback.create_feedback_service")
def test_create_feedback_technician_not_found(mock_create):
    app.dependency_overrides[get_current_user] = customer_user
    mock_create.side_effect = TechnicianNotFoundError(
        "Technician not found."
    )

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 4,
            },
        )

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - CREATE FEEDBACK INVALID RATING
# ============================================================

def test_create_feedback_invalid_rating():
    app.dependency_overrides[get_current_user] = customer_user

    try:
        response = client.post(
            "/feedback",
            json={
                "request_uuid": str(request_uuid),
                "rating": 6,
            },
        )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - VIEW FEEDBACK SUCCESS
# ============================================================

@patch("Api.feedback.get_feedback")
def test_view_feedback_success(mock_get):
    app.dependency_overrides[get_current_user] = customer_user

    mock_get.return_value = {
        "request_uuid": request_uuid,
        "feedback": {
            "feedback_uuid": feedback_uuid,
            "rating": 4.5,
            "comments": "Good service",
            "feedback_date": datetime.now(),
        },
        "technician": {
            "technician_uuid": technician_uuid,
            "technician_name": "Test Technician",
            "rating": 4.5,
        },
    }

    try:
        response = client.get(f"/feedback/{request_uuid}")

        assert response.status_code == 200

        data = response.json()

        assert data["request_uuid"] == str(request_uuid)
        assert data["feedback"]["feedback_uuid"] == str(feedback_uuid)
        assert data["feedback"]["rating"] == "4.5"
        assert data["feedback"]["comments"] == "Good service"
        assert data["technician"]["technician_name"] == "Test Technician"
        assert data["technician"]["rating"] == "4.5"
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - VIEW FEEDBACK NO FEEDBACK
# ============================================================

@patch("Api.feedback.get_feedback")
def test_view_feedback_no_feedback(mock_get):
    app.dependency_overrides[get_current_user] = customer_user

    mock_get.return_value = {
        "request_uuid": request_uuid,
        "message": "No feedback found.",
        "feedback": None,
    }

    try:
        response = client.get(f"/feedback/{request_uuid}")

        assert response.status_code == 200

        data = response.json()

        assert data["request_uuid"] == str(request_uuid)
        assert data["message"] == "No feedback found."
        assert data["feedback"] is None
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - VIEW FEEDBACK REQUEST NOT FOUND
# ============================================================

@patch("Api.feedback.get_feedback")
def test_view_feedback_request_not_found(mock_get):
    app.dependency_overrides[get_current_user] = customer_user
    mock_get.side_effect = ServiceRequestNotFoundError(
        "Service request not found."
    )

    try:
        response = client.get(f"/feedback/{request_uuid}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Service request not found."
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - VIEW FEEDBACK CUSTOMER NOT FOUND
# ============================================================

@patch("Api.feedback.get_feedback")
def test_view_feedback_customer_not_found(mock_get):
    app.dependency_overrides[get_current_user] = customer_user
    mock_get.side_effect = CustomerNotFoundError("Customer not found.")

    try:
        response = client.get(f"/feedback/{request_uuid}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Customer not found."
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - VIEW FEEDBACK TECHNICIAN NOT FOUND
# ============================================================

@patch("Api.feedback.get_feedback")
def test_view_feedback_technician_not_found(mock_get):
    app.dependency_overrides[get_current_user] = technician_user
    mock_get.side_effect = TechnicianNotFoundError("Technician not found.")

    try:
        response = client.get(f"/feedback/{request_uuid}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Technician not found."
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - VIEW FEEDBACK UNAUTHORIZED
# ============================================================

@patch("Api.feedback.get_feedback")
def test_view_feedback_unauthorized(mock_get):
    app.dependency_overrides[get_current_user] = customer_user
    mock_get.side_effect = UnauthorizedFeedbackError(
        "You are not allowed to view this feedback."
    )

    try:
        response = client.get(f"/feedback/{request_uuid}")

        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


# ============================================================
# API - VIEW FEEDBACK INVALID ROLE
# ============================================================

@patch("Api.feedback.get_feedback")
def test_view_feedback_invalid_role(mock_get):
    app.dependency_overrides[get_current_user] = invalid_user
    mock_get.side_effect = InvalidUserRoleError("Invalid user role.")

    try:
        response = client.get(f"/feedback/{request_uuid}")

        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid user role."
    finally:
        app.dependency_overrides.clear()


# ============================================================
# SERVICE - CREATE CUSTOMER NOT FOUND
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_create_feedback_customer_not_found_service(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)
    session.exec.return_value = first_result(None)

    with pytest.raises(CustomerNotFoundError):
        create_feedback(customer_uuid, request_uuid, 4, "Good service")


# ============================================================
# SERVICE - CREATE REQUEST NOT FOUND
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_create_feedback_request_not_found_service(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(None),
    ]

    with pytest.raises(ServiceRequestNotFoundError):
        create_feedback(customer_uuid, request_uuid, 4, "Good service")


# ============================================================
# SERVICE - CREATE UNAUTHORIZED
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_create_feedback_unauthorized_service(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(make_service_request(customer_id=999)),
    ]

    with pytest.raises(UnauthorizedFeedbackError):
        create_feedback(customer_uuid, request_uuid, 4, "Good service")


# ============================================================
# SERVICE - CREATE INCOMPLETE
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_create_feedback_incomplete_service(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(make_service_request(status="IN PROGRESS")),
    ]

    with pytest.raises(IncompleteServiceError):
        create_feedback(customer_uuid, request_uuid, 4, "Good service")


# ============================================================
# SERVICE - CREATE WITHOUT TECHNICIAN
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_create_feedback_no_technician_service(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(make_service_request(technician_id=None)),
    ]

    with pytest.raises(NoTechnicianAssignedError):
        create_feedback(customer_uuid, request_uuid, 4, "Good service")


# ============================================================
# SERVICE - CREATE DUPLICATE
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_create_feedback_duplicate_service(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(make_service_request()),
        first_result(make_feedback()),
    ]

    with pytest.raises(FeedbackAlreadyExistsError):
        create_feedback(customer_uuid, request_uuid, 4, "Good service")


# ============================================================
# SERVICE - CREATE TECHNICIAN NOT FOUND
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_create_feedback_technician_not_found_service(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(make_service_request()),
        first_result(None),
    ]
    session.get.return_value = None

    with pytest.raises(TechnicianNotFoundError):
        create_feedback(customer_uuid, request_uuid, 4, "Good service")


# ============================================================
# SERVICE - CREATE SUCCESS
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_create_feedback_success_service(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    technician = make_technician(rating=4.0)
    feedback_record = make_feedback(rating=4.5, comments="Good service")

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(make_service_request()),
        first_result(None),
        all_result([
            feedback_record,
            SimpleNamespace(rating=None),
        ]),
    ]

    session.get.return_value = technician

    result = create_feedback(
        customer_uuid,
        request_uuid,
        4.5,
        "  Good service  ",
    )

    assert result["message"] == "Feedback submitted successfully."
    assert result["request_uuid"] == request_uuid
    assert result["rating"] == 4.5
    assert result["comments"] == "Good service"
    assert result["technician"]["technician_name"] == "Test Technician"
    assert result["technician"]["rating"] == 4.5
    assert technician.rating == 4.5
    assert session.add.call_count == 2
    assert session.commit.call_count == 2
    assert session.refresh.call_count == 2


# ============================================================
# SERVICE - CREATE WITH NO RATING RECORDS
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_create_feedback_zero_rating_count(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    technician = make_technician(rating=0)

    session.exec.side_effect = [
        first_result(make_customer()),
        first_result(make_service_request()),
        first_result(None),
        all_result([SimpleNamespace(rating=None)]),
    ]

    session.get.return_value = technician

    result = create_feedback(
        customer_uuid,
        request_uuid,
        None,
        None,
    )

    assert result["message"] == "Feedback submitted successfully."
    assert result["comments"] is None
    assert technician.rating == 0


# ============================================================
# SERVICE - GET FEEDBACK REQUEST NOT FOUND
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_request_not_found(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)
    session.exec.return_value = first_result(None)

    with pytest.raises(ServiceRequestNotFoundError):
        get_feedback(customer_uuid, "customer", request_uuid)


# ============================================================
# SERVICE - GET FEEDBACK CUSTOMER NOT FOUND
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_customer_not_found(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_service_request()),
        first_result(None),
    ]

    with pytest.raises(CustomerNotFoundError):
        get_feedback(customer_uuid, "customer", request_uuid)


# ============================================================
# SERVICE - GET FEEDBACK CUSTOMER UNAUTHORIZED
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_customer_unauthorized(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    different_customer = SimpleNamespace(
        customer_id=999,
        customer_uuid=uuid4(),
    )

    session.exec.side_effect = [
        first_result(make_service_request(customer_id=1)),
        first_result(different_customer),
    ]

    with pytest.raises(UnauthorizedFeedbackError):
        get_feedback(customer_uuid, "customer", request_uuid)


# ============================================================
# SERVICE - GET FEEDBACK TECHNICIAN NOT FOUND
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_technician_not_found(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_service_request()),
        first_result(None),
    ]

    with pytest.raises(TechnicianNotFoundError):
        get_feedback(technician_uuid, "technician", request_uuid)


# ============================================================
# SERVICE - GET FEEDBACK TECHNICIAN UNAUTHORIZED
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_technician_unauthorized(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    different_technician = SimpleNamespace(
        technician_id=999,
        technician_uuid=uuid4(),
    )

    session.exec.side_effect = [
        first_result(make_service_request(technician_id=10)),
        first_result(different_technician),
    ]

    with pytest.raises(UnauthorizedFeedbackError):
        get_feedback(technician_uuid, "technician", request_uuid)


# ============================================================
# SERVICE - GET FEEDBACK INVALID ROLE
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_invalid_role(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.return_value = first_result(make_service_request())

    with pytest.raises(InvalidUserRoleError):
        get_feedback(uuid4(), "admin", request_uuid)


# ============================================================
# SERVICE - GET FEEDBACK NO FEEDBACK
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_no_feedback(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_service_request()),
        first_result(make_customer()),
        first_result(None),
    ]

    result = get_feedback(customer_uuid, "customer", request_uuid)

    assert result["request_uuid"] == request_uuid
    assert result["message"] == "No feedback found."
    assert result["feedback"] is None


# ============================================================
# SERVICE - GET FEEDBACK FEEDBACK TECHNICIAN NOT FOUND
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_feedback_technician_not_found(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    session.exec.side_effect = [
        first_result(make_service_request()),
        first_result(make_customer()),
        first_result(make_feedback()),
    ]
    session.get.return_value = None

    with pytest.raises(TechnicianNotFoundError):
        get_feedback(customer_uuid, "customer", request_uuid)


# ============================================================
# SERVICE - GET FEEDBACK SUCCESS AS CUSTOMER
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_success_customer(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    feedback = make_feedback()
    technician = make_technician(rating=4.5)

    session.exec.side_effect = [
        first_result(make_service_request()),
        first_result(make_customer()),
        first_result(feedback),
    ]
    session.get.return_value = technician

    result = get_feedback(customer_uuid, "customer", request_uuid)

    assert result["request_uuid"] == request_uuid
    assert result["feedback"]["feedback_uuid"] == feedback_uuid
    assert result["feedback"]["rating"] == 4.5
    assert result["feedback"]["comments"] == "Good service"
    assert result["technician"]["technician_name"] == "Test Technician"
    assert result["technician"]["rating"] == 4.5


# ============================================================
# SERVICE - GET FEEDBACK SUCCESS AS TECHNICIAN
# ============================================================

@patch("modules.feedback_service.get_session_context")
def test_get_feedback_success_technician(mock_context):
    session = make_session()
    configure_session_context(mock_context, session)

    feedback = make_feedback()
    technician = make_technician(rating=4.5)

    session.exec.side_effect = [
        first_result(make_service_request()),
        first_result(make_technician()),
        first_result(feedback),
    ]
    session.get.return_value = technician

    result = get_feedback(technician_uuid, "technician", request_uuid)

    assert result["request_uuid"] == request_uuid
    assert result["feedback"]["rating"] == 4.5
    assert result["technician"]["technician_name"] == "Test Technician"


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
