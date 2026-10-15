from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app
from Api.dependencies import get_current_user
from tests.mocks.session_mock import ResultMock, SessionMock


client = TestClient(app)


# ============================================================
# HELPERS
# ============================================================

def override_customer():
    return {
        "user_uuid": "customer-test-uuid",
        "role": "customer",
    }


def override_technician():
    return {
        "user_uuid": "technician-test-uuid",
        "role": "technician",
    }


def make_one_result(value):
    result = MagicMock()
    result.one.return_value = value
    result.first.return_value = value
    result.all.return_value = value
    return result


def make_first_result(value):
    result = MagicMock()
    result.first.return_value = value
    result.one.return_value = value
    result.all.return_value = []
    return result


def make_all_result(value):
    result = MagicMock()
    result.all.return_value = value
    result.first.return_value = None
    result.one.return_value = None
    return result


# ============================================================
# SESSION MOCK COVERAGE
# ============================================================

def test_result_mock_first():
    result = ResultMock("test-result")
    assert result.first() == "test-result"


def test_result_mock_all_with_result():
    result = ResultMock(["item1", "item2"])
    assert result.all() == ["item1", "item2"]


def test_result_mock_all_without_result():
    result = ResultMock()
    assert result.all() == []


def test_session_mock_context_manager():
    session = SessionMock()

    with session as active_session:
        assert active_session is session

    assert session.__exit__() is None


def test_session_mock_add_commit_refresh():
    session = SessionMock()
    obj = SimpleNamespace(id=1)

    assert session.add(obj) is None
    assert session.commit() is None
    assert session.refresh(obj) is None


def test_session_mock_get():
    expected = SimpleNamespace(id=1)
    session = SessionMock(get_result=expected)

    assert session.get(None, 1) is expected


def test_session_mock_exec_with_single_result():
    session = SessionMock(result="single-result")
    result = session.exec("query")

    assert result.first() == "single-result"
    assert result.all() == "single-result"


def test_session_mock_exec_with_multiple_results():
    session = SessionMock(
        results=[
            "first-result",
            "second-result",
        ]
    )

    result1 = session.exec("query1")
    result2 = session.exec("query2")

    assert result1.first() == "first-result"
    assert result2.first() == "second-result"
    assert session.exec_count == 2


# ============================================================
# API - GET /reports
# ============================================================

def test_view_reports_success():
    reports = {
        "customer_technician_summary": {
            "total_customers": 5,
            "total_technicians": 3,
            "total_services": 20,
            "total_service_requests": 10,
        },
        "service_request_status": {
            "open_requests": 2,
            "pending_requests": 3,
            "in_progress_requests": 1,
            "completed_requests": 4,
        },
        "service_performance": {
            "most_requested_service": "AC Repair",
            "total_requests_for_service": 5,
        },
        "technician_performance": {
            "highest_rated_technician": "John",
            "highest_rating": Decimal("5.0"),
            "average_technician_rating": 4.2,
        },
        "feedback_summary": {
            "total_feedback": 6,
            "average_customer_rating": 4.3,
        },
        "technician_workload": [
            {
                "technician_id": 1,
                "technician_name": "John",
                "workload": 2,
                "rating": Decimal("5.0"),
            }
        ],
    }

    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = override_technician

    try:
        with patch(
            "Api.reports.get_reports",
            return_value=reports,
        ):
            response = client.get("/reports")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    result = response.json()

    assert result["customer_technician_summary"]["total_customers"] == 5
    assert result["customer_technician_summary"]["total_technicians"] == 3
    assert result["customer_technician_summary"]["total_services"] == 20
    assert result["customer_technician_summary"]["total_service_requests"] == 10

    assert result["service_request_status"]["open_requests"] == 2
    assert result["service_request_status"]["pending_requests"] == 3
    assert result["service_request_status"]["in_progress_requests"] == 1
    assert result["service_request_status"]["completed_requests"] == 4

    assert result["service_performance"]["most_requested_service"] == "AC Repair"
    assert result["service_performance"]["total_requests_for_service"] == 5

    assert result["technician_performance"]["highest_rated_technician"] == "John"
    assert result["technician_performance"]["highest_rating"] == "5.0"
    assert result["technician_performance"]["average_technician_rating"] == 4.2

    assert result["feedback_summary"]["total_feedback"] == 6
    assert result["feedback_summary"]["average_customer_rating"] == 4.3

    assert len(result["technician_workload"]) == 1
    assert result["technician_workload"][0]["technician_id"] == 1
    assert result["technician_workload"][0]["technician_name"] == "John"
    assert result["technician_workload"][0]["workload"] == 2
    assert result["technician_workload"][0]["rating"] == "5.0"


def test_view_reports_customer_denied():
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = override_customer

    try:
        with patch("Api.reports.get_reports") as mock_get_reports:
            response = client.get("/reports")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Technician access required."
    }

    mock_get_reports.assert_not_called()


# ============================================================
# SERVICE - COMPLETE REPORT
# ============================================================

@patch("modules.reports_service.get_session_context")
def test_get_reports_complete_data(mock_get_session_context):
    session = MagicMock()
    mock_get_session_context.return_value.__enter__.return_value = session

    technicians = [
        (1, "John", 5, Decimal("4.5")),
        (2, "David", 3, Decimal("4.0")),
    ]

    session.exec.side_effect = [
        make_one_result(5),                 # total_customers
        make_one_result(3),                 # total_technicians
        make_one_result(20),                # total_services
        make_one_result(10),                # total_requests
        make_one_result(2),                 # open_requests
        make_one_result(3),                 # pending_requests
        make_one_result(1),                 # in_progress_requests
        make_one_result(4),                 # completed_requests
        make_first_result(("AC Repair", 5)),
        make_first_result(("John", Decimal("5.0"))),
        make_one_result(Decimal("4.25")),
        make_one_result(6),
        make_one_result(Decimal("4.35")),
        make_all_result(technicians),
    ]

    from modules.reports_service import get_reports

    result = get_reports()

    assert result["customer_technician_summary"] == {
        "total_customers": 5,
        "total_technicians": 3,
        "total_services": 20,
        "total_service_requests": 10,
    }

    assert result["service_request_status"] == {
        "open_requests": 2,
        "pending_requests": 3,
        "in_progress_requests": 1,
        "completed_requests": 4,
    }

    assert result["service_performance"] == {
        "most_requested_service": "AC Repair",
        "total_requests_for_service": 5,
    }

    assert result["technician_performance"] == {
        "highest_rated_technician": "John",
        "highest_rating": Decimal("5.0"),
        "average_technician_rating": 4.2,
    }

    assert result["feedback_summary"] == {
        "total_feedback": 6,
        "average_customer_rating": 4.3,
    }

    assert result["technician_workload"] == [
        {
            "technician_id": 1,
            "technician_name": "John",
            "workload": 5,
            "rating": Decimal("4.5"),
        },
        {
            "technician_id": 2,
            "technician_name": "David",
            "workload": 3,
            "rating": Decimal("4.0"),
        },
    ]


# ============================================================
# SERVICE - NO MOST REQUESTED / HIGHEST RATED
# ============================================================

@patch("modules.reports_service.get_session_context")
def test_get_reports_no_most_requested_or_highest_rated(
    mock_get_session_context,
):
    session = MagicMock()
    mock_get_session_context.return_value.__enter__.return_value = session

    session.exec.side_effect = [
        make_one_result(0),
        make_one_result(0),
        make_one_result(0),
        make_one_result(0),
        make_one_result(0),
        make_one_result(0),
        make_one_result(0),
        make_one_result(0),
        make_first_result(None),
        make_first_result(None),
        make_one_result(0),
        make_one_result(0),
        make_one_result(0),
        make_all_result([]),
    ]

    from modules.reports_service import get_reports

    result = get_reports()

    assert result["customer_technician_summary"] == {
        "total_customers": 0,
        "total_technicians": 0,
        "total_services": 0,
        "total_service_requests": 0,
    }

    assert result["service_request_status"] == {
        "open_requests": 0,
        "pending_requests": 0,
        "in_progress_requests": 0,
        "completed_requests": 0,
    }

    assert result["service_performance"] == {
        "most_requested_service": None,
        "total_requests_for_service": 0,
    }

    assert result["technician_performance"] == {
        "highest_rated_technician": None,
        "highest_rating": 0,
        "average_technician_rating": 0,
    }

    assert result["feedback_summary"] == {
        "total_feedback": 0,
        "average_customer_rating": 0,
    }

    assert result["technician_workload"] == []


# ============================================================
# SERVICE - NULL AVERAGE VALUES
# ============================================================

@patch("modules.reports_service.get_session_context")
def test_get_reports_null_average_values(mock_get_session_context):
    session = MagicMock()
    mock_get_session_context.return_value.__enter__.return_value = session

    session.exec.side_effect = [
        make_one_result(2),
        make_one_result(1),
        make_one_result(20),
        make_one_result(3),
        make_one_result(1),
        make_one_result(1),
        make_one_result(1),
        make_one_result(0),
        make_first_result(("Plumbing", 2)),
        make_first_result(("Technician One", Decimal("4.0"))),
        make_one_result(None),
        make_one_result(0),
        make_one_result(None),
        make_all_result([]),
    ]

    from modules.reports_service import get_reports

    result = get_reports()

    assert result["technician_performance"] == {
        "highest_rated_technician": "Technician One",
        "highest_rating": Decimal("4.0"),
        "average_technician_rating": 0,
    }

    assert result["feedback_summary"] == {
        "total_feedback": 0,
        "average_customer_rating": 0,
    }


# ============================================================
# SERVICE - WORKLOAD LOOP
# ============================================================

@patch("modules.reports_service.get_session_context")
def test_get_reports_workload_loop(mock_get_session_context):
    session = MagicMock()
    mock_get_session_context.return_value.__enter__.return_value = session

    technicians = [
        (10, "Technician A", 5, Decimal("4.8")),
        (20, "Technician B", 2, Decimal("4.2")),
        (30, "Technician C", 0, Decimal("3.9")),
    ]

    session.exec.side_effect = [
        make_one_result(3),
        make_one_result(3),
        make_one_result(20),
        make_one_result(8),
        make_one_result(2),
        make_one_result(1),
        make_one_result(2),
        make_one_result(3),
        make_first_result(("AC Repair", 4)),
        make_first_result(("Technician A", Decimal("4.8"))),
        make_one_result(Decimal("4.3")),
        make_one_result(7),
        make_one_result(Decimal("4.4")),
        make_all_result(technicians),
    ]

    from modules.reports_service import get_reports

    result = get_reports()

    assert len(result["technician_workload"]) == 3

    assert result["technician_workload"][0] == {
        "technician_id": 10,
        "technician_name": "Technician A",
        "workload": 5,
        "rating": Decimal("4.8"),
    }

    assert result["technician_workload"][1] == {
        "technician_id": 20,
        "technician_name": "Technician B",
        "workload": 2,
        "rating": Decimal("4.2"),
    }

    assert result["technician_workload"][2] == {
        "technician_id": 30,
        "technician_name": "Technician C",
        "workload": 0,
        "rating": Decimal("3.9"),
    }
