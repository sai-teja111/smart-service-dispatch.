
from sqlmodel import text

from Orm.database import get_session_context


MAX_RESULT_ROWS = 100
QUERY_TIMEOUT = "5s"

SENSITIVE_COLUMNS = {
    "password_hash",
}


def execute_query(sql):
    """
    Execute an AI-generated SELECT query using SQLModel.

    PostgreSQL transaction-level read-only protection is an
    additional safeguard. SQL validation and authorization must
    still be enforced before this function is called.
    """

    if not isinstance(sql, str) or not sql.strip():
        return None

    try:
        with get_session_context() as session:

            # Must be the first SQL command in this transaction.
            session.exec(text("SET TRANSACTION READ ONLY"))

            # Prevent a query from running indefinitely.
            session.exec(
                text(
                    f"SET LOCAL statement_timeout = '{QUERY_TIMEOUT}'"
                )
            )

            result = session.exec(text(sql))

            # Fetch at most MAX_RESULT_ROWS rows.
            rows = result.fetchmany(MAX_RESULT_ROWS)

            safe_results = []

            for row in rows:
                row_data = dict(row._mapping)

                # Defense in depth; this does not replace
                # column-level access restrictions.
                for column in SENSITIVE_COLUMNS:
                    row_data.pop(column, None)

                safe_results.append(row_data)

            return safe_results

    except Exception:
        # Avoid exposing database errors or query details to users.
        print("\nAI database query execution failed.")
        return None
