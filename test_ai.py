from Ai.sql_generator import generate_sql
from Ai.sql_validator import validate_sql
from Ai.database import execute_query


question = input(
    "Ask a question about your database: "
)


sql = generate_sql(question)

if not sql:

    print("\nAI could not generate SQL.")
    exit()


print("\n========== GENERATED SQL ==========")
print(sql)


# Step 2: Validate SQL
if not validate_sql(sql):

    print("\nUnsafe SQL query. Execution stopped.")
    exit()


print("\nSQL validation successful.")


# Step 3: Execute SQL
result = execute_query(sql)


# Step 4: Display result
if result is None:

    print("\nNo result returned.")

elif len(result) == 0:

    print("\nNo matching records found.")

else:

    print("\n========== DATABASE RESULT ==========")

    for row in result:

        print(row)