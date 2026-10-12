from  unittest.mock import patch

from Ai.ai_assistant import (
    ai_assistant,
    display_results
)


# ============================================================
# DISPLAY RESULTS - NONE
# ============================================================

def test_display_results_none():

    with patch("builtins.print") as mock_print:

        display_results(None)

    mock_print.assert_not_called()


# ============================================================
# DISPLAY RESULTS - EMPTY
# ============================================================

def test_display_results_empty():

    with patch("builtins.print") as mock_print:

        display_results([])

    mock_print.assert_called_once_with(
        "\nNo records found."
    )


# ============================================================
# DISPLAY RESULTS - RECORDS
# ============================================================

def test_display_results_records():

    results = [
        {
            "customer_id": 1,
            "customer_name": "John"
        },
        {
            "customer_id": 2,
            "customer_name": "David"
        }
    ]

    with patch("builtins.print") as mock_print:

        display_results(results)

    calls = [
        call.args[0]
        for call in mock_print.call_args_list
    ]

    assert (
        "\n========== DATABASE RESULT =========="
        in calls
    )

    assert results[0] in calls

    assert results[1] in calls

    assert (
        "====================================="
        in calls
    )


# ============================================================
# AI ASSISTANT - EXIT
# ============================================================

@patch(
    "builtins.input",
    return_value="exit"
)
def test_ai_assistant_exit(mock_input):

    ai_assistant()

    mock_input.assert_called_once_with(
        "\nYou : "
    )


# ============================================================
# AI ASSISTANT - EMPTY QUESTION
# ============================================================

@patch(
    "builtins.input",
    side_effect=[
        "",
        "exit"
    ]
)
def test_ai_assistant_empty_question(mock_input):

    with patch("builtins.print"):

        ai_assistant()

    assert mock_input.call_count == 2


# ============================================================
# AI ASSISTANT - SQL GENERATION FAILED
# ============================================================

@patch(
    "builtins.input",
    side_effect=[
        "Show customers",
        "exit"
    ]
)
@patch("Ai.ai_assistant.generate_sql")
def test_ai_assistant_sql_generation_failed(
    mock_generate_sql,
    mock_input
):

    mock_generate_sql.return_value = None

    with patch("builtins.print"):

        ai_assistant()

    mock_generate_sql.assert_called_once_with(
        "Show customers"
    )

    assert mock_input.call_count == 2


# ============================================================
# AI ASSISTANT - SQL VALIDATION FAILED
# ============================================================

@patch(
    "builtins.input",
    side_effect=[
        "Show customers",
        "exit"
    ]
)
@patch("Ai.ai_assistant.validate_sql")
@patch("Ai.ai_assistant.generate_sql")
def test_ai_assistant_validation_failed(
    mock_generate_sql,
    mock_validate_sql,
    mock_input
):

    mock_generate_sql.return_value = (
        "SELECT * from  customers;"
    )

    mock_validate_sql.return_value = False

    with patch("builtins.print"):

        ai_assistant()

    mock_generate_sql.assert_called_once_with(
        "Show customers"
    )

    mock_validate_sql.assert_called_once_with(
        "SELECT * from  customers;"
    )

    assert mock_input.call_count == 2


# ============================================================
# AI ASSISTANT - SUCCESSFUL QUERY WITH RESULTS
# ============================================================

@patch(
    "builtins.input",
    side_effect=[
        "Show customers",
        "exit"
    ]
)
@patch("Ai.ai_assistant.execute_query")
@patch("Ai.ai_assistant.validate_sql")
@patch("Ai.ai_assistant.generate_sql")
def test_ai_assistant_success_with_results(
    mock_generate_sql,
    mock_validate_sql,
    mock_execute_query,
    mock_input
):

    sql = "SELECT * from  customers;"

    results = [
        {
            "customer_id": 1,
            "customer_name": "John"
        }
    ]

    mock_generate_sql.return_value = sql
    mock_validate_sql.return_value = True
    mock_execute_query.return_value = results

    with patch("builtins.print"):

        ai_assistant()

    mock_generate_sql.assert_called_once_with(
        "Show customers"
    )

    mock_validate_sql.assert_called_once_with(
        sql
    )

    mock_execute_query.assert_called_once_with(
        sql
    )

    assert mock_input.call_count == 2


# ============================================================
# AI ASSISTANT - SUCCESSFUL QUERY WITH NO RESULTS
# ============================================================

@patch(
    "builtins.input",
    side_effect=[
        "Show customers",
        "exit"
    ]
)
@patch("Ai.ai_assistant.execute_query")
@patch("Ai.ai_assistant.validate_sql")
@patch("Ai.ai_assistant.generate_sql")
def test_ai_assistant_success_no_results(
    mock_generate_sql,
    mock_validate_sql,
    mock_execute_query,
    mock_input
):

    sql = "SELECT * from  customers;"

    mock_generate_sql.return_value = sql
    mock_validate_sql.return_value = True
    mock_execute_query.return_value = []

    with patch("builtins.print"):

        ai_assistant()

    mock_generate_sql.assert_called_once_with(
        "Show customers"
    )

    mock_validate_sql.assert_called_once_with(
        sql
    )

    mock_execute_query.assert_called_once_with(
        sql
    )

    assert mock_input.call_count == 2


# ============================================================
# AI ASSISTANT - QUERY EXECUTION RETURNS NONE
# ============================================================

@patch(
    "builtins.input",
    side_effect=[
        "Show customers",
        "exit"
    ]
)
@patch("Ai.ai_assistant.execute_query")
@patch("Ai.ai_assistant.validate_sql")
@patch("Ai.ai_assistant.generate_sql")
def test_ai_assistant_query_returns_none(
    mock_generate_sql,
    mock_validate_sql,
    mock_execute_query,
    mock_input
):

    sql = "SELECT * from  customers;"

    mock_generate_sql.return_value = sql
    mock_validate_sql.return_value = True
    mock_execute_query.return_value = None

    with patch("builtins.print"):

        ai_assistant()

    mock_generate_sql.assert_called_once_with(
        "Show customers"
    )

    mock_validate_sql.assert_called_once_with(
        sql
    )

    mock_execute_query.assert_called_once_with(
        sql
    )

    assert mock_input.call_count == 2


# ============================================================
# AI ASSISTANT - MULTIPLE QUESTIONS
# ============================================================

@patch(
    "builtins.input",
    side_effect=[
        "Show customers",
        "Show technicians",
        "exit"
    ]
)
@patch("Ai.ai_assistant.execute_query")
@patch("Ai.ai_assistant.validate_sql")
@patch("Ai.ai_assistant.generate_sql")
def test_ai_assistant_multiple_questions(
    mock_generate_sql,
    mock_validate_sql,
    mock_execute_query,
    mock_input
):

    mock_generate_sql.side_effect = [
        "SELECT * from  customers;",
        "SELECT * from  technicians;"
    ]

    mock_validate_sql.side_effect = [
        True,
        True
    ]

    mock_execute_query.side_effect = [
        [
            {
                "customer_id": 1,
                "customer_name": "John"
            }
        ],
        [
            {
                "technician_id": 1,
                "technician_name": "Technician One"
            }
        ]
    ]

    with patch("builtins.print"):

        ai_assistant()

    assert mock_generate_sql.call_count == 2

    assert mock_validate_sql.call_count == 2

    assert mock_execute_query.call_count == 2

    assert mock_input.call_count == 3