"""
SQL Query Execution and Read-Only Security Validation Module.
Ensures safe query execution, restricts destructive operations,
and formats query results into Pandas DataFrames.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import time
from typing import Any, Optional, Tuple
import pandas as pd


@dataclass
class QueryResult:
    """Represents the outcome of a SQL query execution."""
    success: bool
    data: Optional[pd.DataFrame] = None
    row_count: int = 0
    column_count: int = 0
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None
    query: str = ""


class QueryValidator:
    """Validates SQL queries to enforce read-only access and prevent SQL injection or destructive operations."""

    # Disallowed keywords that modify data, structure, or permissions
    FORBIDDEN_KEYWORDS = [
        "DROP",
        "DELETE",
        "TRUNCATE",
        "ALTER",
        "INSERT",
        "UPDATE",
        "CREATE",
        "REPLACE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
        "CALL",
        "VACUUM",
        "ATTACH",
        "DETACH",
        "MERGE",
        "UPSERT",
        "REINDEX",
    ]

    # Permitted starting operations for read-only queries
    ALLOWED_START_KEYWORDS = [
        "SELECT",
        "WITH",
        "EXPLAIN",
        "SHOW",
        "DESCRIBE",
        "DESC",
        "PRAGMA",
    ]

    @classmethod
    def strip_comments(cls, sql: str) -> str:
        """Removes single-line (-- ...) and multi-line (/* ... */) comments from SQL string."""
        # Remove multi-line comments /* ... */
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        # Remove single-line comments -- ...
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        return sql.strip()

    @classmethod
    def validate_query(cls, sql: str) -> Tuple[bool, Optional[str]]:
        """
        Validates whether a SQL query is safe and read-only.
        
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not sql or not sql.strip():
            return False, "Please enter a SQL query."

        cleaned_sql = cls.strip_comments(sql).strip()

        if not cleaned_sql:
            return False, "Please enter a SQL query. The provided query contains only comments or whitespace."

        # Check for multiple statements (semicolon followed by non-whitespace/more text)
        # Ignore semicolons inside string literals
        statements = [s.strip() for s in re.split(r';(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)', cleaned_sql) if s.strip()]
        if len(statements) > 1:
            return False, "Multiple SQL statements detected. Please execute only one SQL statement at a time."

        statement = statements[0] if statements else cleaned_sql

        # Extract tokens/words (ignoring case)
        tokens = re.findall(r'\b[A-Za-z_]+\b', statement)
        if not tokens:
            return False, "Invalid SQL syntax. No valid SQL tokens found."

        first_token = tokens[0].upper()

        if first_token not in cls.ALLOWED_START_KEYWORDS:
            return False, (
                f"Query blocked: '{first_token}' is not permitted. "
                "Only read-only data retrieval queries (e.g., SELECT, WITH) are allowed."
            )

        # Search for forbidden keywords across all tokens
        upper_tokens = [t.upper() for t in tokens]
        for forbidden in cls.FORBIDDEN_KEYWORDS:
            if forbidden in upper_tokens:
                return False, (
                    f"Query blocked: Destructive or modifying operation '{forbidden}' is not permitted. "
                    "This application is strictly configured for read-only queries."
                )

        # Specific check for INTO OUTFILE / INTO DUMPFILE or INTO TABLE
        if re.search(r'\bINTO\s+(OUTFILE|DUMPFILE|TABLE)\b', statement, re.IGNORECASE):
            return False, "Query blocked: Write or export operations using INTO are not permitted."

        return True, None


class QueryExecutor:
    """Executes SQL queries securely against a database connection."""

    @staticmethod
    def execute(conn: Any, db_type: str, query: str) -> QueryResult:
        """
        Validates and executes a SQL query, returning a QueryResult.
        
        Args:
            conn: Active database connection
            db_type: Database type
            query: SQL query text
            
        Returns:
            QueryResult containing status, DataFrame, row count, execution time, or error.
        """
        # Step 1: Read-only query validation
        is_valid, validation_error = QueryValidator.validate_query(query)
        if not is_valid:
            return QueryResult(
                success=False,
                error_message=validation_error,
                query=query
            )

        # Step 2: Execute query with timing
        cleaned_query = QueryValidator.strip_comments(query).rstrip(';').strip()
        start_time = time.perf_counter()

        try:
            # Use pandas read_sql_query for consistent DataFrame formatting
            df = pd.read_sql_query(cleaned_query, conn)
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            return QueryResult(
                success=True,
                data=df,
                row_count=len(df),
                column_count=len(df.columns),
                execution_time_ms=execution_time_ms,
                query=query
            )

        except Exception as e:
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            # Format clean error message
            error_text = str(e).strip()
            # Remove any internal stack or connection string details if present
            if "syntax error" in error_text.lower():
                user_msg = f"SQL Syntax Error: {error_text}"
            elif "no such table" in error_text.lower() or "table" in error_text.lower() and "doesn't exist" in error_text.lower():
                user_msg = f"Table Error: {error_text}"
            elif "no such column" in error_text.lower() or "unknown column" in error_text.lower() or "column" in error_text.lower() and "does not exist" in error_text.lower():
                user_msg = f"Column Error: {error_text}"
            else:
                user_msg = f"Query Execution Error: {error_text}"

            return QueryResult(
                success=False,
                error_message=user_msg,
                execution_time_ms=execution_time_ms,
                query=query
            )


def execute_query(conn: Any, db_type: str, query: str) -> QueryResult:
    """Convenience helper to validate and execute a query."""
    return QueryExecutor.execute(conn, db_type, query)
