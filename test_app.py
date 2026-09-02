"""
Automated Test Suite for SQL Query Explorer.
Tests all 6 specified verification scenarios + additional edge cases.
"""
import os
import unittest
import pandas as pd

from database import DatabaseManager, get_connection, get_tables, get_table_columns
from query_executor import QueryExecutor, QueryValidator, execute_query
from create_sample_db import create_sample_database


class TestSQLQueryExplorer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.db_path = "data/database.db"
        create_sample_database(cls.db_path)
        cls.conn = get_connection(db_type="sqlite", db_path=cls.db_path)

    @classmethod
    def tearDownClass(cls):
        if cls.conn:
            cls.conn.close()

    def test_01_select_limit_10(self):
        """Test 1: SELECT * FROM employees LIMIT 10;"""
        query = "SELECT * FROM employees LIMIT 10;"
        result = execute_query(self.conn, "sqlite", query)
        
        self.assertTrue(result.success, f"Query failed: {result.error_message}")
        self.assertEqual(result.row_count, 10, "Row count should be exactly 10")
        self.assertGreaterEqual(result.column_count, 6, "Employees table should have at least 6 columns")
        self.assertIsNotNone(result.data)
        
        # Verify CSV export contains only those 10 rows (+ 1 header row)
        csv_str = result.data.to_csv(index=False)
        lines = [line for line in csv_str.strip().split("\n") if line]
        self.assertEqual(len(lines), 11, "CSV must contain exactly header + 10 data rows")
        print("[PASS] Test 1: SELECT * FROM employees LIMIT 10 executes and formats correctly.")
    def test_02_select_salary_filter(self):
        """Test 2: SELECT name, salary FROM employees WHERE salary > 50000;"""
        query = "SELECT name, salary FROM employees WHERE salary > 50000;"
        result = execute_query(self.conn, "sqlite", query)
        
        self.assertTrue(result.success, f"Query failed: {result.error_message}")
        self.assertEqual(result.column_count, 2, "Only name and salary columns should be returned")
        self.assertListEqual(list(result.data.columns), ["name", "salary"])
        
        # Verify every returned row satisfies the condition
        for _, row in result.data.iterrows():
            self.assertGreater(float(row["salary"]), 50000.0)
            
        # Verify CSV export contains only filtered records
        csv_str = result.data.to_csv(index=False)
        lines = [line for line in csv_str.strip().split("\n") if line]
        self.assertEqual(len(lines), result.row_count + 1)
        print(f"[PASS] Test 2: Salary filter returned {result.row_count} records (all > $50,000).")

    def test_03_invalid_query_error_handling(self):
        """Test 3: Invalid query SELECT something_that_does_not_exist FROM employees;"""
        query = "SELECT something_that_does_not_exist FROM employees;"
        result = execute_query(self.conn, "sqlite", query)
        
        self.assertFalse(result.success, "Query should fail gracefully")
        self.assertIsNotNone(result.error_message)
        self.assertIn("Column Error", result.error_message)
        self.assertIn("something_that_does_not_exist", result.error_message)
        print(f"[PASS] Test 3: Invalid column produced graceful error: '{result.error_message}'")

    def test_04_empty_query(self):
        """Test 4: Empty query should prompt user to enter a query."""
        for empty_q in ["", "   ", "\n\t  ", "-- just a comment\n"]:
            result = execute_query(self.conn, "sqlite", empty_q)
            self.assertFalse(result.success)
            self.assertIn("Please enter a SQL query", result.error_message)
        print("[PASS] Test 4: Empty queries handled with user-friendly warnings.")

    def test_05_zero_records_returned(self):
        """Test 5: Query that returns no records."""
        query = "SELECT * FROM employees WHERE salary > 99999999;"
        result = execute_query(self.conn, "sqlite", query)
        
        self.assertTrue(result.success, "Query should execute successfully")
        self.assertEqual(result.row_count, 0, "Row count should be 0")
        self.assertIsNotNone(result.data)
        self.assertTrue(result.data.empty)
        print("[PASS] Test 5: Zero-record query returns empty dataframe with success status.")

    def test_06_destructive_query_blocked(self):
        """Test 6: Attempt destructive queries (DROP, DELETE, TRUNCATE, ALTER, INSERT, UPDATE)."""
        destructive_queries = [
            "DROP TABLE employees;",
            "DELETE FROM employees WHERE id = 1;",
            "TRUNCATE TABLE employees;",
            "ALTER TABLE employees ADD COLUMN test VARCHAR(10);",
            "INSERT INTO employees (name, department, salary, hire_date, city) VALUES ('Hacker', 'IT', 100000, '2023-01-01', 'Nowhere');",
            "UPDATE employees SET salary = 1000000;",
            "CREATE TABLE malicious (id INT);",
            "/* comment */ DROP TABLE departments;"
        ]
        
        for q in destructive_queries:
            result = execute_query(self.conn, "sqlite", q)
            self.assertFalse(result.success, f"Destructive query '{q}' should have been blocked!")
            self.assertIn("blocked", result.error_message.lower())
            
        print("[PASS] Test 6: All destructive operations were blocked by read-only validator.")

    def test_07_multi_statement_injection_blocked(self):
        """Test 7: Attempt multi-statement injection."""
        query = "SELECT * FROM employees; DROP TABLE employees;"
        result = execute_query(self.conn, "sqlite", query)
        self.assertFalse(result.success)
        self.assertIn("Multiple SQL statements detected", result.error_message)
        print("[PASS] Test 7: Multi-statement injection attempt blocked.")

    def test_08_schema_introspection(self):
        """Test 8: Database metadata and table introspection without row loading."""
        tables = get_tables(self.conn, "sqlite")
        self.assertIn("employees", tables)
        self.assertIn("departments", tables)
        self.assertIn("customers", tables)
        self.assertIn("products", tables)
        self.assertIn("orders", tables)
        
        schema = get_table_columns(self.conn, "sqlite", "employees")
        self.assertIsInstance(schema, pd.DataFrame)
        cols = list(schema["Column"])
        self.assertIn("id", cols)
        self.assertIn("name", cols)
        self.assertIn("salary", cols)
        self.assertIn("department", cols)
        print("[PASS] Test 8: Schema introspection returns tables and column types.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
