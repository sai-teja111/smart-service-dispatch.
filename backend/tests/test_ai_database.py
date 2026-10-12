
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from Ai.database import execute_query


def create_session_mock(rows=None, execute_error=None):
    """Create a mock SQLModel session and its query result."""
    session = MagicMock()

    if execute_error:
        session.exec.side_effect = execute_error
    else:
        result = MagicMock()
        result.fetchmany.return_value = rows or []

        # The first two exec calls configure the transaction.
        # The third call executes the SELECT query.
        session.exec.side_effect = [
            MagicMock(),
            MagicMock(),
            result,
        ]

    return session


def create_row(**values):
    """Create a row mock compatible with SQLAlchemy/SQLModel results."""
    return SimpleNamespace(_mapping=values)


# ============================================================
# DATABASE - SUCCESS
# ============================================================

@patch("Ai.database.get_session_context")
def test_execute_query_success(mock_get_session_context):
    rows = [
        create_row(customer_id=1, customer_name="John"),
        create_row(customer_id=2, customer_name="David"),
    ]

    session = create_session_mock(rows=rows)

    mock_get_session_context.return_value.__enter__.return_value = session

    result = execute_query("SELECT * FROM customers;")

    assert result == [
        {"customer_id": 1, "customer_name": "John"},
        {"customer_id": 2, "customer_name": "David"},
    ]

    assert session.exec.call_count == 3
    mock_get_session_context.assert_called_once()


# ============================================================
# DATABASE - EMPTY RESULT
# ============================================================

@patch("Ai.database.get_session_context")
def test_execute_query_empty_result(mock_get_session_context):
    session = create_session_mock(rows=[])

    mock_get_session_context.return_value.__enter__.return_value = session

    result = execute_query("SELECT * FROM customers;")

    assert result == []
    assert session.exec.call_count == 3


# ============================================================
# DATABASE - DATABASE ERROR
# ============================================================

@patch("Ai.database.get_session_context")
def test_execute_query_database_error(mock_get_session_context):
    mock_get_session_context.side_effect = Exception(
        "Database connection failed"
    )

    result = execute_query("SELECT * FROM customers;")

    assert result is None


# ============================================================
# DATABASE - EXECUTION ERROR
# ============================================================

@patch("Ai.database.get_session_context")
def test_execute_query_execution_error(mock_get_session_context):
    session = create_session_mock(
        execute_error=Exception("SQL execution failed")
    )

    mock_get_session_context.return_value.__enter__.return_value = session

    result = execute_query("SELECT * FROM customers;")

    assert result is None


# ============================================================
# DATABASE - SENSITIVE COLUMN REMOVAL
# ============================================================

@patch("Ai.database.get_session_context")
def test_execute_query_removes_sensitive_columns(
    mock_get_session_context,
):
    rows = [
        create_row(
            customer_id=1,
            customer_name="John",
            password_hash="sensitive-value",
        )
    ]

    session = create_session_mock(rows=rows)

    mock_get_session_context.return_value.__enter__.return_value = session

    result = execute_query("SELECT * FROM customers;")

    assert result == [
        {"customer_id": 1, "customer_name": "John"}
    ]


# ============================================================
# DATABASE - INVALID QUERY INPUT
# ============================================================

def test_execute_query_rejects_empty_input():
    assert execute_query("") is None
    assert execute_query("   ") is None
    assert execute_query(None) is None
