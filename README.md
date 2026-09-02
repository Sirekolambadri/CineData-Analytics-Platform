# SQL Query Explorer

A clean, interactive, and secure **SQL Query Explorer** web application built with **Python**, **Streamlit**, and **Pandas**. 

The application allows users to connect to SQL databases, inspect table schemas without loading full datasets into memory, write and execute read-only SQL queries, analyze results in an interactive data grid, and download **strictly the result of the executed query** in CSV or Excel formats.

---

## 🚀 Features

- **Multi-Database Support**: Connects seamlessly to SQLite (local file, upload, or pre-built sample database), with extensible connectors for PostgreSQL, MySQL, and Microsoft SQL Server.
- **Interactive Table Explorer**: Browse database tables and inspect column names, data types, nullability, and primary key constraints without fetching entire tables.
- **SQL Query Editor**: Write custom SQL queries with built-in presets and syntax highlighting.
- **Read-Only Security Engine**: Built-in AST/token validation engine that allows data retrieval (`SELECT`, `WITH ... SELECT`, `EXPLAIN`, etc.) while strictly blocking destructive operations (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `INSERT`, `UPDATE`, `CREATE`, etc.).
- **Query Performance Metrics**: Displays row count, column count, and query execution time (ms).
- **Interactive Result Grid**: View returned records in a sortable, searchable Streamlit DataFrame.
- **Isolated Result Exports**: Download **only** the result rows and columns returned by the executed query as **CSV** or **Excel (.xlsx)**.
- **Graceful Error Handling**: User-friendly alerts for syntax errors, missing columns/tables, connection issues, or empty queries without crashing.

---

## 🛠️ Technologies Used

- **Python 3.10+**
- **[Streamlit](https://streamlit.io/)**: Modern Python web application framework
- **[Pandas](https://pandas.pydata.org/)**: High-performance data manipulation and DataFrame formatting
- **[OpenPyXL](https://openpyxl.readthedocs.io/)**: Excel (.xlsx) file generation
- **SQLite3**: Python built-in database engine

---

## 📁 Project Structure

```text
sql_query_explorer/
├── app.py                  # Streamlit UI, page layout, and reactive workflows
├── database.py             # Database connection factory & schema metadata engine
├── query_executor.py       # Query execution, timing, and read-only security validator
├── create_sample_db.py     # Sample database generator utility
├── test_app.py             # Comprehensive automated test suite (8 test cases)
├── requirements.txt        # Minimal Python dependencies
├── README.md               # Project documentation and setup guide
├── .gitignore              # Git ignore rules for virtual envs and credentials
├── data/
│   └── database.db         # Sample SQLite database (employees, orders, etc.)
└── .streamlit/
    ├── config.toml         # Streamlit server & theme configuration
    └── secrets.toml        # Database credentials template (never committed)
```

---

## 📥 Installation

### 1. Clone or Navigate to the Project Directory

```bash
cd d:\SQL
```

### 2. Create and Activate a Virtual Environment

**On Windows (PowerShell / Command Prompt):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

The application will launch and open in your default browser at `http://localhost:8501`.

---

## ⚙️ Database Configuration

### 1. SQLite (Default)
- **Sample Database**: By default, the application uses `data/database.db` which contains realistic tables (`employees`, `departments`, `customers`, `orders`, `products`).
- **Custom File**: Select "Custom Local Path" in the sidebar and enter your `.db` or `.sqlite` file path.
- **File Upload**: Select "Upload .db File" to upload any SQLite database directly from your machine.

### 2. External Databases (PostgreSQL / MySQL / SQL Server)
You can configure database credentials either directly in the sidebar or via `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml

[postgres]
host = "localhost"
port = 5432
database = "my_database"
user = "postgres"
password = "your_secure_password"

[mysql]
host = "localhost"
port = 3306
database = "my_database"
user = "root"
password = "your_secure_password"

[sqlserver]
host = "localhost"
port = 1433
database = "my_database"
user = "sa"
password = "your_secure_password"
```

> **Security Note**: Never commit your real database passwords to version control. The `.gitignore` file is configured to exclude `.streamlit/secrets.toml`.

---

## 📖 Step-by-Step Usage Guide

1. **Connect to Database**: In the left sidebar, choose your database type and confirm the **Connected** status badge.
2. **Explore Tables**: Select a table from the dropdown (e.g. `employees`) to inspect its column names, data types, nullability, and primary key constraints.
3. **Write a SQL Query**: Type your SQL query in the query editor on the main page, or click any of the preset sample query buttons.
4. **Click "Run Query"**: Execute the query securely.
5. **Analyze Results**: View the execution time, returned row count, column count, and the interactive data grid.
6. **Download Results**: Click **📄 Download CSV** or **📊 Download Excel** to save strictly the query results to your computer.

---

## 🧪 Testing

Run the automated test suite to verify all query execution and security scenarios:

```bash
python test_app.py
```

### Verified Test Cases:
1. `SELECT * FROM employees LIMIT 10;` — Verifies limit execution, DataFrame formatting, and row count.
2. `SELECT name, salary FROM employees WHERE salary > 50000;` — Verifies filtering and column subset isolation.
3. `SELECT invalid_column FROM employees;` — Verifies graceful error reporting without application crashes.
4. Empty / Whitespace Queries — Verifies user input validation prompts.
5. Zero-row queries (`WHERE salary > 99999999`) — Verifies empty result handling.
6. Destructive Queries (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `INSERT`, `UPDATE`) — Verifies read-only validator blocks forbidden commands.
7. Multi-statement injection attempts (`SELECT * ...; DROP ...;`) — Verifies single-statement enforcement.
8. Schema Introspection — Verifies table and column type extraction without full-table data loading.
