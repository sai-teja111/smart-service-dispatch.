from Ai.sql_generator import generate_sql
from Ai.sql_validator import validate_sql
from Ai.database import execute_query


def display_results(results):

    if results is None:
        return

    if not results:
        print("\nNo records found.")
        return

    print("\n========== DATABASE RESULT ==========")

    for row in results:
        print(row)

    print("=====================================")


def ai_assistant():

    print(
        "\n=========================================="
    )

    print(
        "        SMART AI DATABASE ASSISTANT"
    )

    print(
        "=========================================="
    )

    print(
        "\nAsk a question about your database."
    )

    print(
        "Type 'exit' to return to the main menu."
    )

    while True:

        question = input(
            "\nYou : "
        ).strip()

        if question.lower() == "exit":

            print(
                "\nReturning to main menu..."
            )

            break

        if not question:

            print(
                "\nPlease enter a question."
            )

            continue

        sql = generate_sql(
            question
        )

        if not sql:
            continue

        print(
            "\nValidating SQL..."
        )

        is_valid = validate_sql(
            sql
        )

        if not is_valid:

            print(
                "\nThe generated SQL did not pass "
                "the safety validation."
            )

            continue

        print(
            "\nSQL validation successful."
        )

        print(
            "\nExecuting query..."
        )

        results = execute_query(
            sql
        )

        display_results(
            results
        )