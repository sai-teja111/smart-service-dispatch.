from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from modules.ai_service import (
    MAX_RESULTS,
    CUSTOMER_HELP,
    TECHNICIAN_HELP,
    _normalize_question,
    _get_help_response,
    _format_help_response,
    _get_user_record_id,
    _get_question_type,
    _build_database_answer,
    answer_ai_question,
)


USER_UUID = uuid4()


class FakeRow(dict):
    """Simulate a database result row with a SQLAlchemy _mapping attribute."""

    @property
    def _mapping(self):
        return self


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def make_db_session(user_record_id=17, rows=None):
    """Create a mocked session with the expected query sequence."""
    session = MagicMock()

    # The application executes:
    # 1. SET TRANSACTION READ ONLY
    # 2. SET LOCAL statement_timeout
    # 3. User ID lookup
    # 4. Main question query
    setup_result_1 = MagicMock()
    setup_result_2 = MagicMock()

    user_lookup_result = MagicMock()
    user_lookup_result.first.return_value = (user_record_id,)

    main_result = MagicMock()
    main_result.fetchmany.return_value = [
        FakeRow(row) for row in (rows or [])
    ]

    session.exec.side_effect = [
        setup_result_1,
        setup_result_2,
        user_lookup_result,
        main_result,
    ]

    return session


# ---------------------------------------------------------
# Question normalization and help responses
# ---------------------------------------------------------

def test_normalize_question():
    assert _normalize_question("  BOOK-A   SERVICE  ") == "book a service"


@pytest.mark.parametrize(
    ("question", "role", "expected_key"),
    [
        ("How do I book a service?", "customer", "book"),
        ("How do I cancel?", "customer", "cancel"),
        ("How do I submit feedback?", "customer", "feedback"),
        ("How do I track my request?", "customer", "track"),
        ("How do I view history?", "customer", "history"),
        ("Customer portal help", "customer", "default"),
        ("Where is the customer?", "technician", "location"),
        ("How do I update a job?", "technician", "status"),
        ("How do I view assigned jobs?", "technician", "jobs"),
        ("How do I view completed jobs?", "technician", "completed"),
        ("Technician portal help", "technician", "default"),
    ],
)
def test_get_help_response(question, role, expected_key):
    help_data = (
        CUSTOMER_HELP if role == "customer" else TECHNICIAN_HELP
    )

    assert _get_help_response(question, role) == help_data[expected_key]


def test_get_help_response_unrecognized_question():
    assert _get_help_response("What is the weather?", "customer") is None


def test_format_help_response():
    result = _format_help_response(
        "How do I book?",
        "Booking guidance",
    )

    assert result == {
        "question": "How do I book?",
        "sql": "",
        "result_count": 0,
        "results": [],
        "answer": "Booking guidance",
    }


# ---------------------------------------------------------
# Database question classification
# ---------------------------------------------------------

@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("Who is the highest rated technician?", "highest_rated_technician"),
        ("How many technicians are registered?", "technician_count"),
        ("How many services are available?", "service_count"),
        ("List available services", "service_catalogue"),
        ("Show my service history", "history"),
        ("How many completed requests do I have?", "completed_count"),
        ("How many pending requests do I have?", "pending_count"),
        ("How many requests do I have?", "count"),
        ("Show my service requests", "list"),
        ("What is the weather today?", None),
    ],
)
def test_get_question_type(question, expected):
    assert _get_question_type(question) == expected


# ---------------------------------------------------------
# User record ID lookup
# ---------------------------------------------------------

def test_get_user_record_id_for_customer():
    session = MagicMock()
    session.exec.return_value.first.return_value = (17,)

    result = _get_user_record_id(
        session,
        "customer",
        USER_UUID,
    )

    assert result == 17
    session.exec.assert_called_once()


def test_get_user_record_id_for_technician():
    session = MagicMock()
    session.exec.return_value.first.return_value = (29,)

    result = _get_user_record_id(
        session,
        "technician",
        USER_UUID,
    )

    assert result == 29


def test_get_user_record_id_not_found():
    session = MagicMock()
    session.exec.return_value.first.return_value = None

    assert _get_user_record_id(
        session,
        "customer",
        USER_UUID,
    ) is None


def test_get_user_record_id_invalid_role():
    with pytest.raises(ValueError, match="Unsupported user role"):
        _get_user_record_id(
            MagicMock(),
            "admin",
            USER_UUID,
        )


# ---------------------------------------------------------
# Human-readable database answers
# ---------------------------------------------------------

@pytest.mark.parametrize(
    ("question_type", "results", "role", "expected"),
    [
        (
            "technician_count",
            [{"technician_count": 3}],
            "customer",
            "There are 3 registered technician(s) in the system.",
        ),
        (
            "technician_count",
            [],
            "customer",
            "There are 0 registered technician(s) in the system.",
        ),
        (
            "service_count",
            [{"service_count": 4}],
            "customer",
            "There are 4 service(s) available in the system.",
        ),
        (
            "service_count",
            [],
            "customer",
            "There are 0 service(s) available in the system.",
        ),
        (
            "service_catalogue",
            [],
            "customer",
            "No services were found in the service catalogue.",
        ),
        (
            "service_catalogue",
            [
                {"skill_name": "AC Repair"},
                {"skill_name": "Plumbing"},
            ],
            "customer",
            "I found 2 service record(s): AC Repair, Plumbing.",
        ),
        (
            "service_catalogue",
            [{"category": "Electrical"}],
            "customer",
            "I found 1 service record(s).",
        ),
        (
            "highest_rated_technician",
            [],
            "customer",
            "No rated technicians were found.",
        ),
        (
            "highest_rated_technician",
            [{"technician_name": "Alex", "rating": 5}],
            "customer",
            "Alex has the highest technician rating: 5/5.",
        ),
        (
            "highest_rated_technician",
            [
                {"technician_name": "Alex", "rating": 5},
                {"technician_name": "Sam", "rating": 5},
            ],
            "customer",
            "Alex, Sam share the highest technician rating: 5/5.",
        ),
        (
            "completed_count",
            [{"request_count": 2}],
            "customer",
            "You have 2 completed service request(s).",
        ),
        (
            "pending_count",
            [{"request_count": 3}],
            "customer",
            "You have 3 pending or in-progress service request(s).",
        ),
        (
            "count",
            [{"request_count": 2}],
            "customer",
            "You have 2 matching service request(s).",
        ),
        (
            "count",
            [{"request_count": 2}],
            "technician",
            "You have 2 matching assigned request(s).",
        ),
        (
            "history",
            [],
            "customer",
            "No service history records were found for your requests.",
        ),
        (
            "history",
            [
                {"old_status": "PENDING"},
                {"old_status": "COMPLETED"},
            ],
            "customer",
            "I found 2 service history record(s) for your requests.",
        ),
        (
            "completed",
            [],
            "customer",
            "You have no completed service requests in the available records.",
        ),
        (
            "completed",
            [{"status": "COMPLETED"}],
            "customer",
            "I found 1 completed service request(s).",
        ),
        (
            "pending",
            [],
            "customer",
            "You have no pending or in-progress service requests in the available records.",
        ),
        (
            "pending",
            [{"status": "PENDING"}],
            "customer",
            "I found 1 pending or in-progress service request(s).",
        ),
        (
            "list",
            [],
            "customer",
            "No matching service requests were found.",
        ),
        (
            "list",
            [{"status": "PENDING"}],
            "customer",
            "I found 1 service request(s) associated with your account.",
        ),
        (
            "unknown",
            [],
            "customer",
            "The query completed successfully.",
        ),
    ],
)
def test_build_database_answer(
    question_type,
    results,
    role,
    expected,
):
    assert _build_database_answer(
        question_type,
        results,
        role,
    ) == expected


# ---------------------------------------------------------
# Main AI service: validation and procedural questions
# ---------------------------------------------------------

@pytest.mark.parametrize("question", ["", "   "])
def test_answer_ai_question_rejects_empty_question(question):
    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        answer_ai_question(question, USER_UUID, "customer")


def test_answer_ai_question_rejects_unsupported_role():
    with pytest.raises(
        PermissionError,
        match="cannot use the AI Assistant",
    ):
        answer_ai_question(
            "Show my requests",
            USER_UUID,
            "admin",
        )


def test_answer_ai_question_rejects_unsupported_question():
    with pytest.raises(ValueError, match="Try asking about"):
        answer_ai_question(
            "What is the weather?",
            USER_UUID,
            "customer",
        )


@patch("modules.ai_service.get_session_context")
def test_answer_ai_question_help_does_not_open_database(mock_context):
    result = answer_ai_question(
        "How do I book a service?",
        USER_UUID,
        "customer",
    )

    assert result["sql"] == ""
    assert result["result_count"] == 0
    assert result["results"] == []
    assert "Customer Dashboard" in result["answer"]
    mock_context.assert_not_called()


# ---------------------------------------------------------
# Main AI service: database question flow
# ---------------------------------------------------------

@patch("modules.ai_service.get_session_context")
def test_answer_ai_question_service_count(mock_context):
    session = make_db_session(
        rows=[{"service_count": 4}],
    )
    mock_context.return_value.__enter__.return_value = session

    result = answer_ai_question(
        "How many services are available?",
        USER_UUID,
        "customer",
    )

    assert result["question"] == "How many services are available?"
    assert result["result_count"] == 1
    assert result["results"] == [{"service_count": 4}]
    assert result["answer"] == (
        "There are 4 service(s) available in the system."
    )
    assert "FROM skills" in result["sql"]
    assert session.exec.call_count == 4


@patch("modules.ai_service.get_session_context")
def test_answer_ai_question_customer_request_count(mock_context):
    session = make_db_session(
        rows=[{"request_count": 2}],
    )
    mock_context.return_value.__enter__.return_value = session

    result = answer_ai_question(
        "How many requests do I have?",
        USER_UUID,
        "customer",
    )

    assert result["result_count"] == 1
    assert "sr.customer_id = :customer_id" in result["sql"]
    assert result["answer"] == (
        "You have 2 matching service request(s)."
    )


@patch("modules.ai_service.get_session_context")
def test_answer_ai_question_technician_request_count(mock_context):
    session = make_db_session(
        rows=[{"request_count": 3}],
    )
    mock_context.return_value.__enter__.return_value = session

    result = answer_ai_question(
        "How many requests do I have?",
        USER_UUID,
        "technician",
    )

    assert "technician_id" in result["sql"]
    assert "assignments" in result["sql"]
    assert result["answer"] == (
        "You have 3 matching assigned request(s)."
    )


@patch("modules.ai_service.get_session_context")
def test_answer_ai_question_user_not_found(mock_context):
    session = make_db_session(user_record_id=None)
    mock_context.return_value.__enter__.return_value = session

    with pytest.raises(
        PermissionError,
        match="account could not be verified",
    ):
        answer_ai_question(
            "How many services are available?",
            USER_UUID,
            "customer",
        )


def test_max_results_constant():
    assert MAX_RESULTS == 100
