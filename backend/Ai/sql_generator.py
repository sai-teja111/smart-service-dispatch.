
import re

from openai import OpenAI

from config import get_settings
from modules.schema_chroma import search_schema


settings = get_settings()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)


def generate_sql(question: str):
    """
    Generate one PostgreSQL SELECT query for the service-dispatch
    database. The generated query must pass sql_validator.py
    before execution.
    """

    if not isinstance(question, str) or not question.strip():
        return None

    try:
        relevant_schema = search_schema(question)

        if not relevant_schema:
            print(
                "\nNo relevant database schema was found "
                "for the supplied question."
            )
            return None

        schema_text = "\n\n".join(relevant_schema)

        database_schema = f"""
You generate PostgreSQL read queries for the Smart Service
Dispatch System.

RELEVANT DATABASE SCHEMA:
{schema_text}

TASK:
Convert the user's database question into one PostgreSQL SELECT
query using only the supplied schema.

STRICT REQUIREMENTS:
1. Return only SQL, with no explanations or Markdown.
2. Generate exactly one SELECT query.
3. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE,
   TRUNCATE, GRANT, REVOKE, or other data-changing statements.
4. Do not generate multiple statements.
5. Use only tables and columns in the supplied schema.
6. Do not invent tables, columns, relationships, or values.
7. Do not use system catalogs or database metadata tables.
8. Do not retrieve password hashes, authentication secrets,
   API keys, tokens, or other credentials.
9. Select only the columns needed to answer the question.
10. Prefer COUNT(*) for count questions.
11. Use appropriate WHERE conditions for requested filters.
12. Use JOIN only when required and when relationships are
    supported by the supplied schema.
13. Do not assume that the requesting user is authorized to
    access every row in a table.
14. Do not attempt to bypass application authorization rules.
15. If the question cannot be answered from the supplied schema,
    return no SQL.

Return only the SQL query.
"""

        print("\nAI is analyzing your question...")

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "system",
                    "content": database_schema,
                },
                {
                    "role": "user",
                    "content": question.strip(),
                },
            ],
            temperature=0,
        )

        if not response.choices:
            print("\nAI did not return a response.")
            return None

        content = response.choices[0].message.content

        if not content or not content.strip():
            print("\nAI did not generate a SQL query.")
            return None

        sql = content.strip()

        # Remove one surrounding Markdown code fence, if present.
        if sql.startswith("```"):
            sql = re.sub(
                r"\A```(?:sql)?\s*",
                "",
                sql,
                count=1,
                flags=re.IGNORECASE,
            )
            sql = re.sub(r"\s*```\s*\Z", "", sql, count=1)
            sql = sql.strip()

        # Basic rejection; sql_validator.py must validate
        # the query structure before database execution.
        if not re.match(r"\ASELECT\b", sql, re.IGNORECASE):
            print("\nThe AI did not return a SELECT query.")
            return None

        # Reject multiple statements and SQL comments.
        if ";" in sql.rstrip(";"):
            print("\nMultiple SQL statements are not allowed.")
            return None

        if re.search(r"--|/\*|\*/", sql):
            print("\nSQL comments are not allowed.")
            return None

        print("\n========== GENERATED SQL ==========")
        print(sql)
        print("===================================")

        return sql

    except Exception:
        # Avoid exposing provider details or credentials.
        print("\nAI SQL generation failed.")
        return None
