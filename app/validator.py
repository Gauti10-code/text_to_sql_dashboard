import re
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DDL, DML


BLOCKED_STATEMENTS = {"DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "REPLACE", "GRANT", "REVOKE"}


class UnsafeSQLError(Exception):
    pass


def extract_sql(raw: str) -> str:
    """
    Strips markdown fences that GPT sometimes wraps around SQL.
    e.g. ```sql SELECT ... ``` → SELECT ...
    """
    raw = raw.strip()
    raw = re.sub(r"^```(?:sql)?", "", raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return raw


def validate_sql(sql: str) -> str:
    """
    Parses and validates SQL. Raises UnsafeSQLError if:
    - query is not a SELECT
    - contains any blocked statement type
    - contains multiple statements (semicolon injection)
    Returns cleaned SQL on success.
    """
    sql = extract_sql(sql)

    # Block multiple statements
    statements = [s for s in sqlparse.parse(sql) if s.get_type() is not None]
    if len(statements) > 1:
        raise UnsafeSQLError("Multiple statements detected. Only single SELECT queries are allowed.")

    if not statements:
        raise UnsafeSQLError("Could not parse SQL statement.")

    stmt: Statement = statements[0]
    stmt_type = stmt.get_type()

    if stmt_type != "SELECT":
        raise UnsafeSQLError(f"Only SELECT queries are allowed. Got: {stmt_type}")

    # Walk all tokens and block any dangerous keywords
    for token in stmt.flatten():
        if token.ttype in (Keyword, DDL, DML):
            if token.normalized.upper() in BLOCKED_STATEMENTS:
                raise UnsafeSQLError(f"Blocked keyword detected: {token.normalized.upper()}")

    # Block comment-based injections
    if re.search(r"(--)|(/\*)", sql):
        raise UnsafeSQLError("SQL comments are not allowed.")

    return sql