from Ai.sql_validator import validate_sql


# ============================================================
# EMPTY / INVALID INPUT
# ============================================================

def test_validate_sql_none():

    assert validate_sql(None) is False


def test_validate_sql_empty_string():

    assert validate_sql("") is False


def test_validate_sql_whitespace():

    assert validate_sql("   ") is False


# ============================================================
# SELECT VALIDATION
# ============================================================

def test_validate_sql_non_select():

    assert validate_sql(
        "UPDATE customers SET customer_name = 'John';"
    ) is False


def test_validate_sql_select_without_table():

    assert validate_sql(
        "SELECT 1;"
    ) is False


def test_validate_sql_valid_select():

    assert validate_sql(
        "SELECT * from  customers;"
    ) is True


def test_validate_sql_select_case_insensitive():

    assert validate_sql(
        "select * from  CUSTOMERS;"
    ) is True


# ============================================================
# ALLOWED TABLES
# ============================================================

def test_validate_sql_customers():

    assert validate_sql(
        "SELECT * from  customers;"
    ) is True


def test_validate_sql_technicians():

    assert validate_sql(
        "SELECT * from  technicians;"
    ) is True


def test_validate_sql_skills():

    assert validate_sql(
        "SELECT * from  skills;"
    ) is True


def test_validate_sql_technician_skills():

    assert validate_sql(
        "SELECT * from  technician_skills;"
    ) is True


def test_validate_sql_service_requests():

    assert validate_sql(
        "SELECT * from  service_requests;"
    ) is True


def test_validate_sql_assignments():

    assert validate_sql(
        "SELECT * from  assignments;"
    ) is True


def test_validate_sql_service_history():

    assert validate_sql(
        "SELECT * from  service_history;"
    ) is True


def test_validate_sql_feedback():

    assert validate_sql(
        "SELECT * from  feedback;"
    ) is True


# ============================================================
# JOIN
# ============================================================

def test_validate_sql_join():

    sql = """
    SELECT
        c.customer_name,
        t.technician_name
    from  customers c
    JOIN technicians t
        ON c.customer_id = t.technician_id;
    """

    assert validate_sql(sql) is True


def test_validate_sql_invalid_join_table():

    sql = """
    SELECT *
    from  customers
    JOIN employee_table
        ON customers.customer_id = employee_table.id;
    """

    assert validate_sql(sql) is False


# ============================================================
# INVALID TABLE
# ============================================================

def test_validate_sql_invalid_table():

    assert validate_sql(
        "SELECT * from  users;"
    ) is False


def test_validate_sql_multiple_tables_with_invalid_table():

    sql = """
    SELECT *
    from  customers
    JOIN users
        ON customers.customer_id = users.id;
    """

    assert validate_sql(sql) is False


# ============================================================
# BLOCKED COMMANDS
# ============================================================

def test_validate_sql_insert():

    assert validate_sql(
        "SELECT * from  customers INSERT INTO users;"
    ) is False


def test_validate_sql_update():

    assert validate_sql(
        "SELECT * from  customers UPDATE customers SET city='Hyderabad';"
    ) is False


def test_validate_sql_delete():

    assert validate_sql(
        "SELECT * from  customers DELETE from  customers;"
    ) is False


def test_validate_sql_drop():

    assert validate_sql(
        "SELECT * from  customers DROP TABLE customers;"
    ) is False


def test_validate_sql_alter():

    assert validate_sql(
        "SELECT * from  customers ALTER TABLE customers ADD COLUMN test TEXT;"
    ) is False


def test_validate_sql_truncate():

    assert validate_sql(
        "SELECT * from  customers TRUNCATE customers;"
    ) is False


def test_validate_sql_create():

    assert validate_sql(
        "SELECT * from  customers CREATE TABLE test;"
    ) is False


def test_validate_sql_grant():

    assert validate_sql(
        "SELECT * from  customers GRANT SELECT ON customers TO user;"
    ) is False


def test_validate_sql_revoke():

    assert validate_sql(
        "SELECT * from  customers REVOKE SELECT ON customers from  user;"
    ) is False


# ============================================================
# MULTIPLE SQL STATEMENTS
# ============================================================

def test_validate_sql_multiple_statements():

    sql = """
    SELECT * from  customers;
    SELECT * from  technicians;
    """

    assert validate_sql(sql) is False


def test_validate_sql_internal_semicolon():

    sql = """
    SELECT *
    from  customers
    WHERE customer_name = 'John;Doe';
    """

    assert validate_sql(sql) is False


# ============================================================
# FORBIDDEN SYSTEM TABLES
# ============================================================

def test_validate_sql_information_schema():

    assert validate_sql(
        "SELECT * from  information_schema;"
    ) is False


def test_validate_sql_pg_catalog():

    assert validate_sql(
        "SELECT * from  pg_catalog;"
    ) is False


def test_validate_sql_pg_tables():

    assert validate_sql(
        "SELECT * from  pg_tables;"
    ) is False


def test_validate_sql_pg_class():

    assert validate_sql(
        "SELECT * from  pg_class;"
    ) is False


def test_validate_sql_pg_database():

    assert validate_sql(
        "SELECT * from  pg_database;"
    ) is False


def test_validate_sql_pg_user():

    assert validate_sql(
        "SELECT * from  pg_user;"
    ) is False


# ============================================================
# INTO
# ============================================================

def test_validate_sql_into():

    assert validate_sql(
        "SELECT * INTO new_table from  customers;"
    ) is False


# ============================================================
# SEMICOLON
# ============================================================

def test_validate_sql_without_final_semicolon():

    assert validate_sql(
        "SELECT * from  customers"
    ) is True


def test_validate_sql_with_final_semicolon():

    assert validate_sql(
        "SELECT * from  customers;"
    ) is True


# ============================================================
# from  TABLE DETECTION
# ============================================================


def test_validate_sql_from_table():
    assert validate_sql(
        "SELECT customer_name from customers;"
    ) is True


    assert validate_sql(
        "SELECT customer_name from  customers;"
    ) is True


def test_validate_sql_join_multiple_allowed_tables():

    sql = """
    SELECT *
    from  customers
    JOIN service_requests
        ON customers.customer_id = service_requests.customer_id
    JOIN skills
        ON service_requests.skill_id = skills.skill_id;
    """

    assert validate_sql(sql) is True

# ============================================================
# FORBIDDEN TABLE NAME DETECTED IN QUERY
# ============================================================

def test_validate_sql_forbidden_table_reference():

    sql = """
    SELECT *
    from  customers
    WHERE customer_name = 'information_schema';
    """

    assert validate_sql(sql) is False