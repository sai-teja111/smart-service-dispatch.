
import re


# ============================================================
# SQL VALIDATION CONFIGURATION
# ============================================================

ALLOWED_TABLES = {
    "customers",
    "technicians",
    "skills",
    "technician_skills",
    "service_requests",
    "assignments",
    "service_history",
    "feedback",
}

FORBIDDEN_TABLES = {
    "information_schema",
    "pg_catalog",
    "pg_tables",
    "pg_class",
    "pg_database",
    "pg_user",
}

FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "MERGE",
    "CALL",
    "EXEC",
    "EXECUTE",
    "COPY",
    "VACUUM",
    "ANALYZE",
    "REFRESH",
    "INTO",
}


# ============================================================
# SQL VALIDATOR
# ============================================================

def validate_sql(sql):
    """
    Validate a single read-only SELECT query.

    Returns:
        True: Query passes the configured validation rules.
        False: Query is empty, invalid, unsafe, or references
               a table that is not approved.
    """

    if not isinstance(sql, str):
        return False

    sql = sql.strip()

    if not sql:
        return False

    # Remove SQL comments while preserving quoted string literals.
    # This prevents blocked keywords from being hidden in comments.
    cleaned = _remove_comments(sql)

    if cleaned is None:
        return False

    cleaned = cleaned.strip()

    if not cleaned:
        return False

    # Reject unbalanced single or double quotes.
    if not _has_balanced_quotes(cleaned):
        return False

    # Reject multiple statements. A single final semicolon is allowed.
    without_final_semicolon = cleaned.rstrip()

    if without_final_semicolon.endswith(";"):
        without_final_semicolon = (
            without_final_semicolon[:-1].rstrip()
        )

    if not without_final_semicolon:
        return False

    if ";" in without_final_semicolon:
        return False

    # The statement must begin with SELECT.
    if not re.match(
        r"^SELECT\b",
        without_final_semicolon,
        flags=re.IGNORECASE,
    ):
        return False

    # Ignore quoted string literals when checking SQL keywords.
    keyword_sql = _mask_quoted_literals(
        without_final_semicolon
    )

    if keyword_sql is None:
        return False

    # Reject blocked commands and SELECT INTO.
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(
            rf"\b{re.escape(keyword)}\b",
            keyword_sql,
            flags=re.IGNORECASE,
        ):
            return False

    # Extract table references from FROM and JOIN clauses.
    table_references = re.findall(
        r"\b(?:FROM|JOIN)\s+"
        r"([a-zA-Z_][a-zA-Z0-9_]*"
        r"(?:\s*\.\s*[a-zA-Z_][a-zA-Z0-9_]*)?)",
        keyword_sql,
        flags=re.IGNORECASE,
    )

    if not table_references:
        return False

    for reference in table_references:
        normalized_reference = re.sub(
            r"\s+",
            "",
            reference,
        ).lower()

        # Schema-qualified references are not permitted.
        if "." in normalized_reference:
            return False

        if normalized_reference in FORBIDDEN_TABLES:
            return False

        if normalized_reference not in ALLOWED_TABLES:
            return False

    # Reject references to forbidden system-table names anywhere
    # in the query, including string literals. This preserves the
    # behavior expected by the supplied forbidden-table test.
    full_sql = cleaned.lower()

    for table in FORBIDDEN_TABLES:
        if re.search(
            rf"\b{re.escape(table)}\b",
            full_sql,
        ):
            return False

    return True


# ============================================================
# SQL COMMENT HANDLING
# ============================================================

def _remove_comments(sql):
    """
    Remove -- and /* ... */ comments without changing quoted strings.

    Return None if a block comment is not terminated.
    """

    output = []
    index = 0
    quote = None
    length = len(sql)

    while index < length:
        char = sql[index]

        if quote:
            output.append(char)

            if char == quote:
                # SQL escapes a quote by doubling it.
                if (
                    index + 1 < length
                    and sql[index + 1] == quote
                ):
                    output.append(sql[index + 1])
                    index += 2
                    continue

                quote = None

            elif char == "\\" and index + 1 < length:
                output.append(sql[index + 1])
                index += 2
                continue

            index += 1
            continue

        if char in ("'", '"'):
            quote = char
            output.append(char)
            index += 1
            continue

        # Single-line comment.
        if sql.startswith("--", index):
            newline = sql.find("\n", index)

            if newline == -1:
                break

            output.append("\n")
            index = newline + 1
            continue

        # Block comment.
        if sql.startswith("/*", index):
            end = sql.find("*/", index + 2)

            if end == -1:
                return None

            output.append(" ")
            index = end + 2
            continue

        output.append(char)
        index += 1

    if quote:
        return None

    return "".join(output)


def _has_balanced_quotes(sql):
    """Check that single and double quotes are balanced."""

    quote = None
    index = 0

    while index < len(sql):
        char = sql[index]

        if quote:
            if char == quote:
                if (
                    index + 1 < len(sql)
                    and sql[index + 1] == quote
                ):
                    index += 2
                    continue

                quote = None

            elif char == "\\" and index + 1 < len(sql):
                index += 2
                continue

        elif char in ("'", '"'):
            quote = char

        index += 1

    return quote is None


def _mask_quoted_literals(sql):
    """
    Replace quoted literal contents with spaces.

    Preserve positions so keyword and table-reference checks do
    not mistake text inside a literal for SQL syntax.
    """

    output = []
    quote = None
    index = 0

    while index < len(sql):
        char = sql[index]

        if quote:
            if char == quote:
                if (
                    index + 1 < len(sql)
                    and sql[index + 1] == quote
                ):
                    output.extend([" ", " "])
                    index += 2
                    continue

                quote = None

            output.append(" ")
            index += 1
            continue

        if char in ("'", '"'):
            quote = char
            output.append(" ")
        else:
            output.append(char)

        index += 1

    if quote:
        return None

    return "".join(output)
