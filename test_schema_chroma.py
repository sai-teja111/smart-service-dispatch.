from modules.schema_chroma import (
    load_schema_to_chroma,
    search_schema
)


print(
    "\nLoading database schema into Chroma..."
)


load_schema_to_chroma()


print(
    "\n=========================================="
)

print(
    "       DATABASE SCHEMA SEARCH"
)

print(
    "=========================================="
)


question = input(
    "\nEnter your database question : "
)


results = search_schema(
    question
)


if results:

    print(
        "\n========== RELEVANT SCHEMA =========="
    )


    for index, document in enumerate(
        results,
        start=1
    ):

        print(
            f"\n---------- RESULT {index} ----------"
        )

        print(
            document
        )


else:

    print(
        "\nNo relevant schema found."
    )