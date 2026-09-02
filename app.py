"""
SQL Query Explorer - Streamlit Web Application
A clean, interactive, read-only SQL query explorer and data extraction tool.
"""
from __future__ import annotations

import io
import os
import tempfile
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from database import DatabaseManager
from query_executor import QueryExecutor, QueryResult


# Set Streamlit Page Configuration
st.set_page_config(
    page_title="SQL Query Explorer",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished aesthetics
st.markdown("""
<style>
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
        color: #38BDF8;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Code Editor Styling */
    .stTextArea textarea {
        font-family: 'Fira Code', 'Consolas', 'Courier New', monospace;
        font-size: 0.95rem;
        line-height: 1.5;
        border-radius: 8px;
    }
    
    /* Badge styling */
    .status-badge-connected {
        display: inline-flex;
        align-items: center;
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ADE80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .status-badge-disconnected {
        display: inline-flex;
        align-items: center;
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State Variables
if "query_result" not in st.session_state:
    st.session_state.query_result: Optional[QueryResult] = None
if "current_query" not in st.session_state:
    st.session_state.current_query = "SELECT * FROM employees LIMIT 10;"
if "uploaded_db_path" not in st.session_state:
    st.session_state.uploaded_db_path = None
if "selected_sample_query" not in st.session_state:
    st.session_state.selected_sample_query = None


def get_excel_bytes(df: pd.DataFrame) -> bytes:
    """Converts a pandas DataFrame to an Excel xlsx binary stream."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Query_Result')
    return output.getvalue()


# ---------------------------------------------------------
# SIDEBAR: Database Configuration & Table Explorer
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🗄️ Database Connection")
    
    db_type = st.selectbox(
        "Database Type",
        options=["SQLite", "PostgreSQL", "MySQL", "SQL Server"],
        index=2,
        help="Select the SQL database type you wish to query."
    ).lower()

    connection_params: Dict[str, Any] = {}
    sqlite_db_path = "data/database.db"

    if db_type == "sqlite":
        source_mode = st.radio(
            "SQLite Source",
            options=["Default Sample DB", "Custom Local Path", "Upload .db File"],
            index=0,
            horizontal=False
        )

        if source_mode == "Default Sample DB":
            sqlite_db_path = "data/database.db"
            if not os.path.exists(sqlite_db_path):
                # Auto-create sample DB if not exists
                try:
                    from create_sample_db import create_sample_database
                    create_sample_database(sqlite_db_path)
                except Exception as e:
                    st.error(f"Could not initialize sample DB: {e}")

        elif source_mode == "Custom Local Path":
            sqlite_db_path = st.text_input(
                "Database File Path",
                value="data/database.db",
                help="Absolute or relative path to the SQLite .db file."
            )

        elif source_mode == "Upload .db File":
            uploaded_file = st.file_uploader("Upload SQLite Database (.db, .sqlite)", type=["db", "sqlite", "sqlite3"])
            if uploaded_file is not None:
                # Save to a temporary file
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, f"uploaded_{uploaded_file.name}")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.uploaded_db_path = temp_path
                sqlite_db_path = temp_path
            elif st.session_state.uploaded_db_path and os.path.exists(st.session_state.uploaded_db_path):
                sqlite_db_path = st.session_state.uploaded_db_path
            else:
                sqlite_db_path = ""

    else:
        # Client-server database configuration
        # Attempt to pull from st.secrets if present
        default_host = "localhost"
        default_port = 5432 if db_type == "postgresql" else (3306 if db_type == "mysql" else 1433)
        default_db = "movies_bookig_db"
        default_user = "postgres" if db_type == "postgresql" else ("root" if db_type == "mysql" else "sa")
        
        try:
            if db_type in st.secrets:
                secret_cfg = st.secrets[db_type]
                default_host = secret_cfg.get("host", default_host)
                default_port = int(secret_cfg.get("port", default_port))
                default_db = secret_cfg.get("database", default_db)
                default_user = secret_cfg.get("user", default_user)
        except Exception:
            pass

        with st.expander("Connection Settings", expanded=True):
            col_host, col_port = st.columns([2, 1])
            with col_host:
                host = st.text_input("Host", value=default_host)
            with col_port:
                port = st.number_input("Port", value=default_port, step=1)
            database = st.text_input("Database Name", value=default_db)
            user = st.text_input("Username", value=default_user)
            password = st.text_input("Password", type="password")

            connection_params = {
                "host": host,
                "port": port,
                "database": database,
                "user": user,
                "password": password
            }

    # Connection Test & Status
    st.markdown("---")
    conn_valid = False
    conn_message = ""
    active_conn = None

    try:
        if db_type == "sqlite" and not sqlite_db_path:
            conn_valid = False
            conn_message = "Please select or upload a SQLite database file."
        else:
            conn_valid, conn_message = DatabaseManager.test_connection(
                db_type=db_type,
                db_path=sqlite_db_path,
                connection_params=connection_params
            )
            if conn_valid:
                active_conn = DatabaseManager.get_connection(
                    db_type=db_type,
                    db_path=sqlite_db_path,
                    connection_params=connection_params
                )
    except Exception as e:
        conn_valid = False
        conn_message = str(e)

    # Status indicator
    if conn_valid:
        st.markdown(
            '<div class="status-badge-connected">● Connected</div>',
            unsafe_allow_html=True
        )
        if db_type == "sqlite":
            st.caption(f"📁 **File:** `{os.path.basename(sqlite_db_path)}`")
        else:
            st.caption(f"🌐 **Server:** `{connection_params.get('host')}:{connection_params.get('port')}/{connection_params.get('database')}`")
    else:
        st.markdown(
            '<div class="status-badge-disconnected">● Disconnected</div>',
            unsafe_allow_html=True
        )
        st.caption(f"⚠️ {conn_message}")

    # ---------------------------------------------------------
    # TABLE EXPLORER
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📋 Table Explorer")

    tables: List[str] = []
    if conn_valid and active_conn is not None:
        try:
            tables = DatabaseManager.get_tables(active_conn, db_type)
        except Exception as e:
            st.error(f"Error reading tables: {e}")

    if tables:
        st.caption(f"Found **{len(tables)}** table{'s' if len(tables) != 1 else ''}:")
        selected_table = st.selectbox(
            "Select a table to inspect:",
            options=tables,
            index=0
        )

        if selected_table:
            try:
                # Column metadata inspection (does not load table data)
                schema_df = DatabaseManager.get_table_columns(active_conn, db_type, selected_table)
                st.markdown(f"**Columns in `{selected_table}`:**")
                st.dataframe(
                    schema_df,
                    use_container_width=True,
                    hide_index=True
                )

                # Quick helper buttons for query building
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"🔍 Query `{selected_table}`", use_container_width=True):
                        st.session_state.current_query = f"SELECT * FROM {selected_table} LIMIT 10;"
                        st.rerun()
                with col_btn2:
                    if st.button(f"📊 Count Rows", use_container_width=True):
                        st.session_state.current_query = f"SELECT COUNT(*) AS total_rows FROM {selected_table};"
                        st.rerun()

            except Exception as e:
                st.error(f"Could not load schema: {e}")
    else:
        if conn_valid:
            st.info("No user tables found in database.")
        else:
            st.info("Connect to a database to explore tables.")


# ---------------------------------------------------------
# MAIN PAGE: Query Editor & Execution Results
# ---------------------------------------------------------
st.title("🗄️ SQL Query Explorer")
st.markdown("Write and execute SQL queries to analyze data and download custom result sets.")

# Sample Query Presets
with st.expander("💡 Quick Sample Queries (Click to load)", expanded=False):
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        if st.button("👥 Top 10 Employees", use_container_width=True):
            st.session_state.current_query = "SELECT * FROM employees LIMIT 10;"
            st.rerun()
        if st.button("💰 Employees Salary > $50k", use_container_width=True):
            st.session_state.current_query = "SELECT name, department, salary FROM employees WHERE salary > 50000 ORDER BY salary DESC;"
            st.rerun()
    with q_col2:
        if st.button("🏢 Dept Avg Salary", use_container_width=True):
            st.session_state.current_query = "SELECT department, COUNT(*) AS headcount, ROUND(AVG(salary), 2) AS avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC;"
            st.rerun()
        if st.button("📦 Low Stock Products", use_container_width=True):
            st.session_state.current_query = "SELECT product_name, category, price, stock_quantity FROM products WHERE stock_quantity < 50 ORDER BY stock_quantity ASC;"
            st.rerun()
    with q_col3:
        if st.button("🔗 Join Orders & Customers", use_container_width=True):
            st.session_state.current_query = "SELECT o.order_id, c.name AS customer_name, c.country, o.order_date, o.total_amount, o.status FROM orders o JOIN customers c ON o.customer_id = c.customer_id ORDER BY o.order_date DESC;"
            st.rerun()
        if st.button("🚫 Test Security (Blocked)", use_container_width=True):
            st.session_state.current_query = "DROP TABLE employees;"
            st.rerun()

# SQL Query Editor Section
st.subheader("SQL Query Editor")
query_input = st.text_area(
    label="Enter your SQL query below:",
    value=st.session_state.current_query,
    height=150,
    help="Enter read-only SQL queries (SELECT, WITH, EXPLAIN). Destructive statements (DROP, DELETE, etc.) will be blocked."
)

col_run, col_clear, _ = st.columns([1.5, 1, 6])
with col_run:
    run_clicked = st.button("🚀 Run Query", type="primary", use_container_width=True)
with col_clear:
    if st.button("🧹 Clear", use_container_width=True):
        st.session_state.current_query = ""
        st.session_state.query_result = None
        st.rerun()

# Handle Query Execution
if run_clicked:
    st.session_state.current_query = query_input
    
    if not query_input or not query_input.strip():
        st.session_state.query_result = QueryResult(
            success=False,
            error_message="Please enter a SQL query.",
            query=""
        )
    elif not conn_valid or active_conn is None:
        st.session_state.query_result = QueryResult(
            success=False,
            error_message=f"Unable to connect to database: {conn_message}",
            query=query_input
        )
    else:
        # Execute query securely
        result = QueryExecutor.execute(
            conn=active_conn,
            db_type=db_type,
            query=query_input
        )
        st.session_state.query_result = result

# Close active connection at end of request cycle
if active_conn is not None:
    try:
        active_conn.close()
    except Exception:
        pass


# ---------------------------------------------------------
# QUERY RESULTS DISPLAY & DOWNLOAD SECTION
# ---------------------------------------------------------
st.markdown("---")
st.subheader("Query Result")

if st.session_state.query_result is not None:
    result = st.session_state.query_result

    if not result.success:
        # Display clean, informative error message
        st.error(f"❌ {result.error_message}")
        if result.execution_time_ms > 0:
            st.caption(f"Execution failed in {result.execution_time_ms} ms")

    else:
        # Query succeeded!
        st.success("✅ Query executed successfully.")

        # Display performance and dimension metrics
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(label="Rows Returned", value=f"{result.row_count:,}")
        with m_col2:
            st.metric(label="Columns", value=f"{result.column_count:,}")
        with m_col3:
            st.metric(label="Execution Time", value=f"{result.execution_time_ms:.2f} ms")

        # Zero rows condition
        if result.row_count == 0:
            st.info("ℹ️ The query executed successfully, but no records were returned.")
            if result.data is not None and not result.data.empty:
                st.dataframe(result.data, use_container_width=True)

        else:
            # Display interactive result table
            st.dataframe(
                result.data,
                use_container_width=True,
                height=min(400, 38 * (result.row_count + 1) + 20)
            )

            # ---------------------------------------------------------
            # DOWNLOAD ONLY THE CURRENT QUERY RESULT
            # ---------------------------------------------------------
            st.markdown("#### 📥 Download Query Result")
            st.caption("Export strictly the rows and columns returned by the executed query above:")

            csv_data = result.data.to_csv(index=False).encode('utf-8')
            
            d_col1, d_col2, _ = st.columns([1.5, 1.5, 4])
            with d_col1:
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name="query_result.csv",
                    mime="text/csv",
                    type="secondary",
                    use_container_width=True,
                    help="Download current query result as a CSV file"
                )

            with d_col2:
                try:
                    excel_data = get_excel_bytes(result.data)
                    st.download_button(
                        label="📊 Download Excel",
                        data=excel_data,
                        file_name="query_result.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="secondary",
                        use_container_width=True,
                        help="Download current query result as an Excel file"
                    )
                except Exception as ex:
                    st.warning(f"Excel export unavailable: {ex}")

else:
    st.info("Write a SQL query above and click **🚀 Run Query** to view results.")
