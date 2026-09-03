"""
CineData Analytics Platform
An Interactive SQL-Based Movie Booking Data Analysis System

Main Streamlit Application Entrypoint.
"""

import io
import streamlit as st
import pandas as pd
from database import (
    DB_NAME,
    get_connection,
    test_connection,
    get_tables,
    get_table_columns,
    parse_mysql_error
)
from query_executor import execute_query, validate_query, ALLOWED_COMMANDS


# -----------------------------------------------------------------------------
# 1. Page Configuration and Theming
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CineData Analytics Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, clean UI appearance
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #E50914;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .card {
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        background-color: #ffffff;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Session State Initialization
# -----------------------------------------------------------------------------
if "is_connected" not in st.session_state:
    st.session_state.is_connected = False
if "db_creds" not in st.session_state:
    st.session_state.db_creds = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": ""
    }
if "discovered_tables" not in st.session_state:
    st.session_state.discovered_tables = []
if "query_result_df" not in st.session_state:
    st.session_state.query_result_df = None
if "query_result_msg" not in st.session_state:
    st.session_state.query_result_msg = ""
if "query_result_success" not in st.session_state:
    st.session_state.query_result_success = None
if "query_text_val" not in st.session_state:
    st.session_state.query_text_val = "SELECT * FROM movies LIMIT 10;"


# -----------------------------------------------------------------------------
# 3. Helper Functions for Downloads
# -----------------------------------------------------------------------------
@st.cache_data
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Converts DataFrame to UTF-8 encoded CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


@st.cache_data
def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """Converts DataFrame to Excel bytes using openpyxl."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="QueryResult")
    return output.getvalue()


# -----------------------------------------------------------------------------
# 4. Header Section
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">🎬 CineData Analytics Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">An Interactive SQL-Based Movie Booking Data Analysis System</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. Sidebar: MySQL Connection Manager
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("🔌 MySQL Connection")
    st.markdown("Enter your MySQL credentials to connect to the movie booking database.")

    # Fixed Database indicator
    st.text_input("Database Name", value=DB_NAME, disabled=True, help="Fixed target database for this project.")

    # Input credentials
    input_host = st.text_input("MySQL Host", value=st.session_state.db_creds["host"], placeholder="localhost")
    input_port = st.number_input("MySQL Port", value=int(st.session_state.db_creds["port"]), min_value=1, max_value=65535, step=1)
    input_user = st.text_input("MySQL Username", value=st.session_state.db_creds["user"], placeholder="root")
    input_password = st.text_input("MySQL Password", value=st.session_state.db_creds["password"], type="password", placeholder="Enter password")

    col_btn1, col_btn2 = st.columns([1, 1])

    with col_btn1:
        if st.button("Connect to MySQL", type="primary", use_container_width=True):
            if not input_user.strip():
                st.error("Please provide a valid MySQL username.")
            else:
                with st.spinner("Connecting to MySQL..."):
                    success, msg = test_connection(
                        host=input_host,
                        port=input_port,
                        user=input_user,
                        password=input_password
                    )
                    if success:
                        st.session_state.is_connected = True
                        st.session_state.db_creds = {
                            "host": input_host.strip(),
                            "port": int(input_port),
                            "user": input_user.strip(),
                            "password": input_password
                        }
                        # Retrieve and store discovered tables
                        try:
                            conn = get_connection(
                                host=input_host,
                                port=input_port,
                                user=input_user,
                                password=input_password
                            )
                            st.session_state.discovered_tables = get_tables(conn)
                            conn.close()
                            st.success("Connected successfully!")
                        except Exception as e:
                            st.error(f"Error loading tables: {parse_mysql_error(e)}")
                    else:
                        st.session_state.is_connected = False
                        st.session_state.discovered_tables = []
                        st.error(msg)

    with col_btn2:
        if st.button("Disconnect", use_container_width=True, disabled=not st.session_state.is_connected):
            st.session_state.is_connected = False
            st.session_state.discovered_tables = []
            st.session_state.query_result_df = None
            st.session_state.query_result_msg = ""
            st.session_state.query_result_success = None
            st.info("Disconnected from MySQL.")

    st.divider()

    # Connection Status Widget
    if st.session_state.is_connected:
        st.markdown(
            f'<div class="status-badge status-connected">● Connected to {DB_NAME}</div>',
            unsafe_allow_html=True
        )
        st.caption(f"Host: `{st.session_state.db_creds['host']}:{st.session_state.db_creds['port']}` | User: `{st.session_state.db_creds['user']}`")

        # Display discovered tables in sidebar
        st.markdown("### 📋 Discovered Tables")
        if st.session_state.discovered_tables:
            for t in st.session_state.discovered_tables:
                st.markdown(f"- `{t}`")
        else:
            st.warning("No tables found in this database.")
    else:
        st.markdown(
            '<div class="status-badge status-disconnected">○ Not Connected</div>',
            unsafe_allow_html=True
        )
        st.caption("Please provide credentials and click 'Connect to MySQL' to begin.")


# -----------------------------------------------------------------------------
# 6. Main Content Area
# -----------------------------------------------------------------------------
if not st.session_state.is_connected:
    st.info(
        "👋 **Welcome to CineData Analytics Platform!**\n\n"
        "To get started:\n"
        "1. Enter your MySQL Server connection details in the sidebar on the left.\n"
        "2. Click **Connect to MySQL**.\n"
        f"3. The application will connect directly to the **`{DB_NAME}`** database and load your tables.\n\n"
        "*Note: If you have not yet created the database on your MySQL server, you can import the provided `movies_bookig_db.sql` file.*"
    )

    # Display database architecture preview
    st.markdown("### 🗂️ Target Database Architecture")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Target Database:** `movies_bookig_db`
        
        **Standard Schema Tables:**
        1. `theatres` — Cinema branches, locations, and total screens
        2. `screens` — Screen auditoriums, seating capacities, and screen types (IMAX, Dolby, etc.)
        3. `movies` — Movie catalogue with genres, durations, ratings, and release dates
        4. `customers` — Customer user profiles, emails, phones, and cities
        5. `bookings` — Ticket booking transactions, show timings, payment & booking statuses
        """)
    with col2:
        st.markdown("""
        **🛡️ Built-in Analytics Security:**
        - **Read-Only Engine:** Allows `SELECT`, `WITH`, `EXPLAIN`, `SHOW`, `DESCRIBE`.
        - **Destructive Query Protection:** Blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, etc.
        - **Multi-statement Protection:** Prevents SQL injection chains.
        - **Strict Database Scope:** Only accesses metadata belonging to `movies_bookig_db`.
        """)

else:
    # -------------------------------------------------------------------------
    # Section A: Database & Table Explorer
    # -------------------------------------------------------------------------
    st.markdown("## 🔍 Database Tables Explorer")
    
    if not st.session_state.discovered_tables:
        st.warning(f"No tables discovered in `{DB_NAME}`. Please verify that the database contains tables.")
    else:
        selected_table = st.selectbox(
            "Select a table to inspect its schema and column details:",
            options=st.session_state.discovered_tables,
            index=0
        )

        if selected_table:
            try:
                conn = get_connection(
                    host=st.session_state.db_creds["host"],
                    port=st.session_state.db_creds["port"],
                    user=st.session_state.db_creds["user"],
                    password=st.session_state.db_creds["password"]
                )
                columns_df = get_table_columns(conn, selected_table)
                conn.close()

                col_exp1, col_exp2 = st.columns([3, 1])
                with col_exp1:
                    st.caption(f"Showing columns for table: **`{selected_table}`**")
                    st.dataframe(columns_df, use_container_width=True, hide_index=True)
                with col_exp2:
                    st.markdown("**Quick Action:**")
                    if st.button(f"Load query for `{selected_table}`", use_container_width=True):
                        st.session_state.query_text_val = f"SELECT * FROM {selected_table} LIMIT 10;"
                        st.rerun()

            except Exception as e:
                st.error(f"Failed to inspect columns for table '{selected_table}': {parse_mysql_error(e)}")

    st.divider()

    # -------------------------------------------------------------------------
    # Section B: SQL Query Editor
    # -------------------------------------------------------------------------
    st.markdown("## 💻 SQL Query Editor")
    st.caption("Write and execute read-only SQL queries against `movies_bookig_db`.")

    # Quick Query Presets for College / Demo presentation
    with st.expander("💡 Preset SQL Query Templates (Click to apply)", expanded=False):
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            if st.button("Top Rated Movies", use_container_width=True):
                st.session_state.query_text_val = "SELECT title, genre, rating, language, release_date FROM movies ORDER BY rating DESC LIMIT 5;"
                st.rerun()
            if st.button("High Capacity Screens", use_container_width=True):
                st.session_state.query_text_val = "SELECT s.screen_name, s.screen_type, s.seating_capacity, t.theatre_name, t.city FROM screens s JOIN theatres t ON s.theatre_id = t.theatre_id ORDER BY s.seating_capacity DESC;"
                st.rerun()
        with p_col2:
            if st.button("Recent Bookings Summary", use_container_width=True):
                st.session_state.query_text_val = "SELECT b.booking_id, c.full_name, m.title, b.show_time, b.seats_booked, b.total_amount, b.payment_status FROM bookings b JOIN customers c ON b.customer_id = c.customer_id JOIN movies m ON b.movie_id = m.movie_id ORDER BY b.booking_date DESC LIMIT 10;"
                st.rerun()
            if st.button("Revenue by Movie", use_container_width=True):
                st.session_state.query_text_val = "SELECT m.title, COUNT(b.booking_id) AS total_bookings, SUM(b.seats_booked) AS total_tickets_sold, SUM(b.total_amount) AS total_revenue FROM movies m LEFT JOIN bookings b ON m.movie_id = b.movie_id GROUP BY m.movie_id, m.title ORDER BY total_revenue DESC;"
                st.rerun()
        with p_col3:
            if st.button("Customer Booking Activity", use_container_width=True):
                st.session_state.query_text_val = "SELECT c.customer_id, c.full_name, c.city, COUNT(b.booking_id) AS total_bookings, COALESCE(SUM(b.total_amount), 0) AS total_spent FROM customers c LEFT JOIN bookings b ON c.customer_id = b.customer_id GROUP BY c.customer_id, c.full_name, c.city ORDER BY total_spent DESC;"
                st.rerun()
            if st.button("Reset to Default", use_container_width=True):
                st.session_state.query_text_val = "SELECT * FROM movies LIMIT 10;"
                st.rerun()

    # Query Input Text Area
    user_query = st.text_area(
        label="Write your SQL query:",
        value=st.session_state.query_text_val,
        height=140,
        help="Allowed statements: SELECT, WITH, EXPLAIN, SHOW, DESCRIBE, DESC. Destructive queries (INSERT, UPDATE, DELETE, DROP) are blocked."
    )

    # Run Query Button
    col_run, col_info = st.columns([1, 4])
    with col_run:
        run_clicked = st.button("▶ Run Query", type="primary", use_container_width=True)
    with col_info:
        st.markdown(
            "<span style='color: #28a745; font-size: 0.9rem;'>🛡️ Read-Only Mode Active</span> &nbsp;|&nbsp; "
            "<span style='color: #6c757d; font-size: 0.9rem;'>Allowed: SELECT, WITH, EXPLAIN, SHOW, DESCRIBE</span>",
            unsafe_allow_html=True
        )

    if run_clicked:
        st.session_state.query_text_val = user_query
        
        # Validate query first
        is_valid, validation_msg = validate_query(user_query)
        if not is_valid:
            st.session_state.query_result_success = False
            st.session_state.query_result_msg = validation_msg
            st.session_state.query_result_df = None
        else:
            with st.spinner("Executing query on MySQL..."):
                try:
                    conn = get_connection(
                        host=st.session_state.db_creds["host"],
                        port=st.session_state.db_creds["port"],
                        user=st.session_state.db_creds["user"],
                        password=st.session_state.db_creds["password"]
                    )
                    success, df, row_count, exec_time, msg = execute_query(conn, user_query)
                    conn.close()

                    st.session_state.query_result_success = success
                    st.session_state.query_result_msg = msg
                    st.session_state.query_result_df = df if success else None

                except Exception as e:
                    st.session_state.query_result_success = False
                    st.session_state.query_result_msg = f"Connection error during query execution: {parse_mysql_error(e)}"
                    st.session_state.query_result_df = None

    # -------------------------------------------------------------------------
    # Section C: Query Results Display
    # -------------------------------------------------------------------------
    if st.session_state.query_result_success is not None:
        st.markdown("## 📊 Query Results")

        if st.session_state.query_result_success:
            st.success(st.session_state.query_result_msg)

            df_result = st.session_state.query_result_df
            if df_result is not None:
                if len(df_result) > 0:
                    st.dataframe(df_result, use_container_width=True)
                else:
                    st.info("Query executed successfully, but returned 0 rows.")
                    if len(df_result.columns) > 0:
                        st.dataframe(df_result, use_container_width=True)

                # -----------------------------------------------------------------
                # Section D: Download Query Result
                # -----------------------------------------------------------------
                st.markdown("### 📥 Download Query Result")
                st.caption("Export the current query result to CSV or Excel format.")

                col_dl1, col_dl2, col_dl_space = st.columns([1, 1, 2])

                with col_dl1:
                    csv_data = convert_df_to_csv(df_result)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv_data,
                        file_name="cinedata_query_result.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                with col_dl2:
                    try:
                        excel_data = convert_df_to_excel(df_result)
                        st.download_button(
                            label="📊 Download Excel",
                            data=excel_data,
                            file_name="cinedata_query_result.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.warning(f"Excel export unavailable: {e}")

        else:
            # Query was either blocked by validator or produced MySQL error
            if "Operation Blocked" in st.session_state.query_result_msg or "Safety Warning" in st.session_state.query_result_msg:
                st.warning(f"⚠️ {st.session_state.query_result_msg}")
            else:
                st.error(f"❌ {st.session_state.query_result_msg}")


# -----------------------------------------------------------------------------
# 7. Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888888; font-size: 0.85rem;'>"
    "CineData Analytics Platform &bull; College Project &bull; Powered by Python, Streamlit & MySQL"
    "</div>",
    unsafe_allow_html=True
)
