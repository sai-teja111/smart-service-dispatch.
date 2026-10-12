from  types import SimpleNamespace
from  unittest.mock import patch

from Ai.sql_generator import generate_sql


# ============================================================
# HELPER
# ============================================================

def mock_openai_response(
    content=None,
    choices=True
):
    if not choices:
        return SimpleNamespace(
            choices=[]
        )

    message = SimpleNamespace(
        content=content
    )

    choice = SimpleNamespace(
        message=message
    )

    return SimpleNamespace(
        choices=[choice]
    )


# ============================================================
# SCHEMA NOT FOUND
# ============================================================

@patch("Ai.sql_generator.search_schema")
def test_generate_sql_schema_not_found(
    mock_search_schema
):

    mock_search_schema.return_value = []

    result = generate_sql(
        "Show customers"
    )

    assert result is None

    mock_search_schema.assert_called_once_with(
        "Show customers"
    )


# ============================================================
# SUCCESSFUL SQL GENERATION
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_success(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name, phone)"
    ]

    mock_create.return_value = mock_openai_response(
        "SELECT * from  customers;"
    )

    result = generate_sql(
        "Show all customers"
    )

    assert result == (
        "SELECT * from  customers;"
    )

    mock_search_schema.assert_called_once_with(
        "Show all customers"
    )

    mock_create.assert_called_once()


# ============================================================
# MULTIPLE SCHEMA RESULTS
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_multiple_schema_results(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)",
        "service_requests(request_id, customer_id)",
        "skills(skill_id, skill_name)"
    ]

    mock_create.return_value = mock_openai_response(
        "SELECT * from  customers;"
    )

    result = generate_sql(
        "Show customers"
    )

    assert result == (
        "SELECT * from  customers;"
    )

    mock_create.assert_called_once()


# ============================================================
# AI RETURNS NO CHOICES
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_no_choices(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)"
    ]

    mock_create.return_value = mock_openai_response(
        choices=False
    )

    result = generate_sql(
        "Show customers"
    )

    assert result is None


# ============================================================
# AI RETURNS EMPTY CONTENT
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_empty_content(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)"
    ]

    mock_create.return_value = mock_openai_response(
        content=""
    )

    result = generate_sql(
        "Show customers"
    )

    assert result is None


# ============================================================
# AI RETURNS NONE CONTENT
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_none_content(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)"
    ]

    mock_create.return_value = mock_openai_response(
        content=None
    )

    result = generate_sql(
        "Show customers"
    )

    assert result is None


# ============================================================
# MARKDOWN SQL RESPONSE
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_markdown_sql(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)"
    ]

    mock_create.return_value = mock_openai_response(
        content="""```sql
SELECT * from  customers;
```"""
    )

    result = generate_sql(
        "Show all customers"
    )

    assert result == (
        "SELECT * from  customers;"
    )


# ============================================================
# MARKDOWN SQL UPPERCASE
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_markdown_sql_uppercase(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)"
    ]

    mock_create.return_value = mock_openai_response(
        content="""```SQL
SELECT customer_name
from  customers;
```"""
    )

    result = generate_sql(
        "Show customer names"
    )

    assert result == (
        "SELECT customer_name\n"
        "from  customers;"
    )


# ============================================================
# SQL WITH WHITESPACE
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_strips_whitespace(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)"
    ]

    mock_create.return_value = mock_openai_response(
        content="   SELECT * from  customers;   "
    )

    result = generate_sql(
        "Show customers"
    )

    assert result == (
        "SELECT * from  customers;"
    )


# ============================================================
# NON-SELECT RESPONSE
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_non_select(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)"
    ]

    mock_create.return_value = mock_openai_response(
        "UPDATE customers SET customer_name = 'John';"
    )

    result = generate_sql(
        "Change customer name"
    )

    assert result is None


# ============================================================
# AI RESPONSE WITH NORMAL TEXT
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_invalid_text_response(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)"
    ]

    mock_create.return_value = mock_openai_response(
        "I cannot answer that question."
    )

    result = generate_sql(
        "What is the weather?"
    )

    assert result is None


# ============================================================
# OPENROUTER / OPENAI ERROR
# ============================================================

@patch("Ai.sql_generator.client.chat.completions.create")
@patch("Ai.sql_generator.search_schema")
def test_generate_sql_api_error(
    mock_search_schema,
    mock_create
):

    mock_search_schema.return_value = [
        "customers(customer_id, customer_name)"
    ]

    mock_create.side_effect = Exception(
        "OpenRouter connection failed"
    )

    result = generate_sql(
        "Show customers"
    )

    assert result is None


# ============================================================
# CHROMA / SCHEMA SEARCH ERROR
# ============================================================

@patch("Ai.sql_generator.search_schema")
def test_generate_sql_schema_search_error(
    mock_search_schema
):

    mock_search_schema.side_effect = Exception(
        "ChromaDB error"
    )

    result = generate_sql(
        "Show customers"
    )

    assert result is None