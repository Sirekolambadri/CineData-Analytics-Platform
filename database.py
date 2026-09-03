"""
Database Module for CineData Analytics Platform.
Handles MySQL connections and metadata discovery for `movies_bookig_db`.
"""

import pymysql
import pymysql.cursors
import pandas as pd
from typing import Tuple, List, Optional, Any

# Constant: Fixed database name as mandated
DB_NAME = "movies_bookig_db"


def parse_mysql_error(err: Exception) -> str:
    """
    Translates raw MySQL / PyMySQL exceptions into beginner-friendly error messages.
    Ensures passwords or sensitive strings are never exposed.
    """
    if isinstance(err, pymysql.err.OperationalError):
        code, msg = err.args if len(err.args) >= 2 else (0, str(err))
        if code == 1045:
            return "Access Denied: Please check your MySQL Username and Password."
        elif code == 2003:
            return "Connection Failed: Could not connect to MySQL server. Ensure MySQL is running and the Host/Port are correct."
        elif code == 1049:
            return f"Database Not Found: The database '{DB_NAME}' does not exist on your MySQL server. Please import the provided 'movies_bookig_db.sql' file."
        elif code == 2005:
            return "Unknown Host: The specified MySQL Host name could not be resolved."
        return f"MySQL Operational Error ({code}): {msg}"
    elif isinstance(err, pymysql.err.ProgrammingError):
        code, msg = err.args if len(err.args) >= 2 else (0, str(err))
        return f"MySQL Programming Error ({code}): {msg}"
    elif isinstance(err, pymysql.err.InternalError):
        code, msg = err.args if len(err.args) >= 2 else (0, str(err))
        return f"MySQL Internal Error ({code}): {msg}"
    return f"Connection Error: {str(err)}"


def get_connection(
    host: str = "localhost",
    port: int = 3306,
    user: str = "root",
    password: str = "",
    database: str = DB_NAME,
    connect_timeout: int = 5
) -> pymysql.Connection:
    """
    Establishes and returns a PyMySQL connection to the MySQL database.
    """
    try:
        connection = pymysql.connect(
            host=host.strip() if host else "localhost",
            port=int(port) if port else 3306,
            user=user.strip() if user else "root",
            password=password,
            database=database,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=connect_timeout,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        friendly_error = parse_mysql_error(e)
        raise ConnectionError(friendly_error) from None


def test_connection(
    host: str,
    port: int,
    user: str,
    password: str
) -> Tuple[bool, str]:
    """
    Tests the MySQL connection by connecting and running 'SELECT 1;'.
    Returns (True, success_message) or (False, error_message).
    """
    conn = None
    try:
        conn = get_connection(
            host=host,
            port=port,
            user=user,
            password=password,
            database=DB_NAME
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
        return True, f"Successfully connected to database '{DB_NAME}' on {host}:{port}."
    except Exception as e:
        return False, parse_mysql_error(e)
    finally:
        if conn and conn.open:
            conn.close()


def get_tables(connection: pymysql.Connection) -> List[str]:
    """
    Discovers base tables belonging EXCLUSIVELY to the current database (movies_bookig_db).
    Never queries or returns tables from other schemas.
    """
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            # Extract table names from dict cursor results
            tables = [list(r.values())[0] for r in rows]
            return tables
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve tables: {parse_mysql_error(e)}") from None


def get_table_columns(connection: pymysql.Connection, table_name: str) -> pd.DataFrame:
    """
    Retrieves column metadata for a given table strictly within the current database.
    Returns a Pandas DataFrame formatted for display.
    """
    query = """
        SELECT
            column_name AS `Column Name`,
            data_type AS `Data Type`,
            is_nullable AS `Nullable`,
            column_key AS `Key Type`,
            column_type AS `Full Data Type`
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
        ORDER BY ordinal_position;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (table_name,))
            rows = cursor.fetchall()
            if rows:
                df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame(columns=[
                    "Column Name", "Data Type", "Nullable", "Key Type", "Full Data Type"
                ])
            return df
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve columns for '{table_name}': {parse_mysql_error(e)}") from None
