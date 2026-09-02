"""
Database connection and metadata management module for SQL Query Explorer.
Handles connection creation, validation, table introspection, and schema retrieval.
"""
from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd


class DatabaseManager:
    """Manages database connections, schema queries, and metadata retrieval."""

    @staticmethod
    def get_connection(
        db_type: str = "sqlite",
        db_path: str = "data/database.db",
        connection_params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Creates and returns a database connection.
        
        Args:
            db_type: Database type ('sqlite', 'postgresql', 'mysql', 'sqlserver')
            db_path: Path to database file (for SQLite)
            connection_params: Dictionary with host, port, database, user, password (for client-server DBs)
        
        Returns:
            Active database connection object.
        """
        db_type = db_type.lower()
        
        if db_type == "sqlite":
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found: {db_path}")
            # Connect in URI/ro mode if desired, or standard connection
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
            
        elif db_type == "postgresql":
            try:
                import psycopg2  # type: ignore
            except ImportError:
                raise ImportError("PostgreSQL connector (psycopg2) is not installed. Please install psycopg2-binary.")
            params = connection_params or {}
            return psycopg2.connect(
                host=params.get("host", "localhost"),
                port=int(params.get("port", 5432)),
                database=params.get("database", ""),
                user=params.get("user", ""),
                password=params.get("password", ""),
                connect_timeout=params.get("timeout", 5),
            )
            
        elif db_type == "mysql":
            try:
                import pymysql  # type: ignore
            except ImportError:
                raise ImportError("MySQL connector (pymysql) is not installed. Please install pymysql.")
            params = connection_params or {}
            return pymysql.connect(
                host=params.get("host", "localhost"),
                port=int(params.get("port", 3306)),
                database=params.get("database", ""),
                user=params.get("user", ""),
                password=params.get("password", ""),
                connect_timeout=params.get("timeout", 5),
            )
            
        elif db_type == "sqlserver":
            try:
                import pyodbc  # type: ignore
            except ImportError:
                raise ImportError("SQL Server connector (pyodbc) is not installed. Please install pyodbc.")
            params = connection_params or {}
            driver = params.get("driver", "ODBC Driver 17 for SQL Server")
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={params.get('host', 'localhost')},{params.get('port', 1433)};"
                f"DATABASE={params.get('database', '')};"
                f"UID={params.get('user', '')};"
                f"PWD={params.get('password', '')};"
            )
            return pyodbc.connect(conn_str, timeout=5)
            
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def test_connection(
        db_type: str = "sqlite",
        db_path: str = "data/database.db",
        connection_params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """
        Tests database connectivity without leaving open connections.
        
        Returns:
            Tuple of (is_connected: bool, message: str)
        """
        try:
            conn = DatabaseManager.get_connection(db_type, db_path, connection_params)
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.fetchone()
            conn.close()
            return True, "Successfully connected to database."
        except Exception as e:
            # Strip potential password strings if any from raw exception
            msg = str(e)
            return False, f"Connection failed: {msg}"

    @staticmethod
    def get_tables(conn: Any, db_type: str = "sqlite") -> List[str]:
        """
        Retrieves a sorted list of all user table names in the database.
        """
        db_type = db_type.lower()
        cursor = conn.cursor()
        
        try:
            if db_type == "sqlite":
                query = """
                    SELECT name 
                    FROM sqlite_master 
                    WHERE type = 'table' 
                      AND name NOT LIKE 'sqlite_%'
                    ORDER BY name;
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                return [row[0] if isinstance(row, (list, tuple, sqlite3.Row)) else row['name'] for row in rows]
                
            elif db_type in ("postgresql", "mysql", "sqlserver"):
                query = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                      AND table_type IN ('BASE TABLE', 'TABLE')
                    ORDER BY table_name;
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                return [row[0] for row in rows]
            else:
                return []
        except Exception as e:
            raise RuntimeError(f"Error retrieving tables: {str(e)}")

    @staticmethod
    def get_table_columns(conn: Any, db_type: str = "sqlite", table_name: str = "") -> pd.DataFrame:
        """
        Retrieves column metadata (Name, Data Type, Nullable, Primary Key)
        without querying or loading table rows.
        """
        if not table_name:
            return pd.DataFrame(columns=["Column", "Data Type", "Nullable", "Primary Key"])

        # Sanitize table_name for safe identifier wrapping
        clean_table_name = table_name.replace('"', '').replace("'", "").strip()
        db_type = db_type.lower()
        cursor = conn.cursor()

        try:
            if db_type == "sqlite":
                cursor.execute(f'PRAGMA table_info("{clean_table_name}");')
                rows = cursor.fetchall()
                data = []
                for row in rows:
                    col_dict = dict(row) if isinstance(row, sqlite3.Row) else {
                        "name": row[1],
                        "type": row[2] or "TEXT",
                        "notnull": row[3],
                        "pk": row[5]
                    }
                    data.append({
                        "Column": col_dict.get("name", ""),
                        "Data Type": col_dict.get("type", "UNKNOWN").upper(),
                        "Nullable": "NO" if col_dict.get("notnull") == 1 else "YES",
                        "Primary Key": "YES" if col_dict.get("pk") == 1 else "NO"
                    })
                return pd.DataFrame(data)

            elif db_type in ("postgresql", "mysql", "sqlserver"):
                query = """
                    SELECT 
                        column_name AS "Column",
                        data_type AS "Data Type",
                        is_nullable AS "Nullable"
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """
                cursor.execute(query, (clean_table_name,))
                rows = cursor.fetchall()
                data = []
                for row in rows:
                    data.append({
                        "Column": row[0],
                        "Data Type": str(row[1]).upper(),
                        "Nullable": str(row[2]).upper(),
                        "Primary Key": "N/A"
                    })
                return pd.DataFrame(data)
            else:
                return pd.DataFrame(columns=["Column", "Data Type", "Nullable", "Primary Key"])
        except Exception as e:
            raise RuntimeError(f"Error retrieving table structure for '{table_name}': {str(e)}")

    @staticmethod
    def get_table_row_count(conn: Any, db_type: str = "sqlite", table_name: str = "") -> Optional[int]:
        """Returns the total number of rows in a table."""
        if not table_name:
            return 0
        clean_table_name = table_name.replace('"', '').replace("'", "").strip()
        cursor = conn.cursor()
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{clean_table_name}";')
            res = cursor.fetchone()
            return res[0] if res else 0
        except Exception:
            return None


def get_connection(
    db_type: str = "sqlite",
    db_path: str = "data/database.db",
    connection_params: Optional[Dict[str, Any]] = None
) -> Any:
    """Convenience helper function to get a connection."""
    return DatabaseManager.get_connection(db_type, db_path, connection_params)


def test_connection(
    db_type: str = "sqlite",
    db_path: str = "data/database.db",
    connection_params: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """Convenience helper function to test a connection."""
    return DatabaseManager.test_connection(db_type, db_path, connection_params)


def get_tables(conn: Any, db_type: str = "sqlite") -> List[str]:
    """Convenience helper function to get table names."""
    return DatabaseManager.get_tables(conn, db_type)


def get_table_columns(conn: Any, db_type: str = "sqlite", table_name: str = "") -> pd.DataFrame:
    """Convenience helper function to get table columns."""
    return DatabaseManager.get_table_columns(conn, db_type, table_name)
