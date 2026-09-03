"""
Query Executor and Safety Validator Module for CineData Analytics Platform.
Enforces read-only execution, blocks destructive statements, and executes SQL against MySQL.
"""

import re
import time
import pymysql
import pandas as pd
from typing import Tuple, Optional, Any

# Whitelisted read-only commands
ALLOWED_COMMANDS = {"SELECT", "WITH", "EXPLAIN", "SHOW", "DESCRIBE", "DESC"}

# Blacklisted destructive and modifying SQL keywords
FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "REPLACE", "GRANT", "REVOKE", "CALL", "EXEC",
    "EXECUTE", "LOCK", "UNLOCK", "RENAME", "SET", "FLUSH",
    "SHUTDOWN", "KILL", "RESET"
}


def strip_sql_comments(sql: str) -> str:
    """
    Removes SQL comments (single-line -- or #, and multi-line /* ... */)
    to inspect the actual executable SQL text.
    """
    # Remove block comments /* ... */
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    # Remove single line comments starting with -- or #
    sql = re.sub(r"(--|#).*$", "", sql, flags=re.MULTILINE)
    return sql.strip()


def remove_string_literals(sql: str) -> str:
    """
    Replaces string literals ('...' and "...") with whitespace
    so keyword checks do not false-positive on data values.
    """
    # Replace single quoted strings (handling escaped quotes)
    sql = re.sub(r"'(''|[^'])*'", " '' ", sql)
    # Replace double quoted strings
    sql = re.sub(r'"(""|[^"])*"', ' "" ', sql)
    return sql


def validate_query(raw_query: str) -> Tuple[bool, str]:
    """
    Validates that a query is non-empty, contains only a single SQL statement,
    starts with an allowed read-only verb, and contains no forbidden destructive commands.
    """
    if not raw_query or not raw_query.strip():
        return False, "Query cannot be empty. Please enter a valid SQL query."

    # Strip comments
    cleaned_sql = strip_sql_comments(raw_query)
    if not cleaned_sql:
        return False, "Query contains only comments. Please enter an executable SQL query."

    # Strip string literals for safe lexical analysis
    sanitized_sql = remove_string_literals(cleaned_sql)

    # Check for multiple statements separated by semicolons
    # Semicolons inside string literals were already removed by remove_string_literals
    statements = [s.strip() for s in sanitized_sql.split(";") if s.strip()]
    if len(statements) > 1:
        return False, (
            "Safety Warning: Multiple SQL statements are not permitted in a single run. "
            "Please execute one query at a time."
        )

    if not statements:
        return False, "No executable SQL statement found."

    single_stmt = statements[0]

    # Extract the first keyword/verb of the query
    match = re.match(r"^\s*([A-Za-z]+)", single_stmt)
    if not match:
        return False, "Unable to identify SQL command verb. Please check your query syntax."

    first_keyword = match.group(1).upper()

    # Check whitelist
    if first_keyword not in ALLOWED_COMMANDS:
        return False, (
            f"Operation Blocked: '{first_keyword}' statements are not permitted. "
            "This application operates in READ-ONLY mode. "
            f"Allowed statements: {', '.join(sorted(ALLOWED_COMMANDS))}."
        )

    # Check blacklist for forbidden keywords anywhere in the sanitized query
    tokens = re.findall(r"\b[A-Za-z_]+\b", single_stmt)
    upper_tokens = {t.upper() for t in tokens}

    for forbidden in FORBIDDEN_KEYWORDS:
        if forbidden in upper_tokens:
            return False, (
                f"Operation Blocked: Destructive or modifying keyword '{forbidden}' is not permitted. "
                "Only read-only queries (SELECT, WITH, EXPLAIN, SHOW, DESCRIBE) are allowed."
            )

    return True, ""


def execute_query(
    connection: pymysql.Connection,
    query_str: str
) -> Tuple[bool, Optional[pd.DataFrame], int, float, str]:
    """
    Validates and executes a read-only SQL query against the MySQL database.
    Returns:
        (success: bool, df: Optional[pd.DataFrame], row_count: int, execution_time: float, message: str)
    """
    is_valid, validation_msg = validate_query(query_str)
    if not is_valid:
        return False, None, 0, 0.0, validation_msg

    start_time = time.perf_counter()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query_str)
            # Fetch all rows
            rows = cursor.fetchall()
            execution_time = time.perf_counter() - start_time

            if rows:
                df = pd.DataFrame(rows)
            else:
                # If query returned no rows, retrieve column names from cursor description
                if cursor.description:
                    col_names = [col[0] for col in cursor.description]
                    df = pd.DataFrame(columns=col_names)
                else:
                    df = pd.DataFrame()

            row_count = len(df)
            msg = f"Query executed successfully in {execution_time:.4f} seconds. {row_count} row(s) returned."
            return True, df, row_count, execution_time, msg

    except pymysql.MySQLError as e:
        execution_time = time.perf_counter() - start_time
        # Extract MySQL error code and description
        code = e.args[0] if len(e.args) > 0 else "N/A"
        err_text = e.args[1] if len(e.args) > 1 else str(e)
        return False, None, 0, execution_time, f"MySQL Error [{code}]: {err_text}"
    except Exception as e:
        execution_time = time.perf_counter() - start_time
        return False, None, 0, execution_time, f"Execution Error: {str(e)}"
