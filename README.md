# 🎬 CineData Analytics Platform
> **An Interactive SQL-Based Movie Booking Data Analysis System**

A clean, modern, and beginner-friendly Streamlit application designed for querying, exploring, and analyzing movie booking datasets directly from an existing **MySQL** database.

---

## 📌 Project Overview

The **CineData Analytics Platform** acts as an interactive SQL bridge between data analysts/students and a production-grade MySQL movie booking database. It enables users to securely connect, inspect live database tables and schema structures, execute analytical read-only SQL queries, and export query results to CSV and Excel formats.

### 🔑 Key Principles
- **Direct MySQL Connection**: Connects in real-time to MySQL using PyMySQL.
- **Dedicated Target Database**: Operates strictly on `movies_bookig_db` (intentional spelling).
- **Strict Table Scope**: Queries database metadata (`information_schema`) filtered strictly to the active database.
- **Built-in Safety & Security**: Enforces read-only execution mode (`SELECT`, `WITH`, `EXPLAIN`, `SHOW`, `DESCRIBE`) while disallowing destructive operations (`INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.) and multi-statement injection chains.
- **No Hardcoded Secrets**: MySQL passwords are never stored in code, configuration files, or version control.

---

## 🏗️ Architecture & Project Structure

```text
CineData-Analytics-Platform/
│
├── app.py                  # Streamlit frontend, connection manager, UI layout & exports
├── database.py             # PyMySQL connection handler and scoped information_schema discovery
├── query_executor.py       # SQL validator, read-only safety enforcer & DataFrame query runner
├── requirements.txt        # Minimal Python dependencies
├── README.md               # Comprehensive project documentation & user guide
├── .gitignore              # Git ignore rules for environments, caches & secrets
└── movies_bookig_db.sql    # Database schema export & backup for MySQL initialization
```

---

## 🗄️ Database Schema (`movies_bookig_db`)

The database consists of **five core relational tables**:

| Table Name | Description | Key Attributes |
| :--- | :--- | :--- |
| **`theatres`** | Cinema complexes and venue locations | `theatre_id`, `theatre_name`, `city`, `state`, `address`, `total_screens` |
| **`screens`** | Individual auditoriums and tech formats | `screen_id`, `theatre_id`, `screen_name`, `seating_capacity`, `screen_type` |
| **`movies`** | Movie catalogue and rating records | `movie_id`, `title`, `genre`, `duration_minutes`, `release_date`, `rating`, `language` |
| **`customers`** | Registered moviegoers and patron info | `customer_id`, `full_name`, `email`, `phone`, `city`, `registration_date` |
| **`bookings`** | Ticket reservations and transactions | `booking_id`, `customer_id`, `movie_id`, `screen_id`, `show_time`, `total_amount`, `payment_status` |

---

## 🛠️ Technology Stack

- **Frontend & Interface**: [Streamlit](https://streamlit.io/)
- **Database Engine**: [MySQL Server](https://www.mysql.com/)
- **Database Driver**: [PyMySQL](https://github.com/PyMySQL/PyMySQL)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/)
- **Spreadsheet Export**: [OpenPyXL](https://openpyxl.readthedocs.io/)
- **Auth Security**: [Cryptography](https://cryptography.io/) (for MySQL 8+ `caching_sha2_password`)

---

## ⚙️ Prerequisites

Before running the platform, ensure you have:
1. **Python 3.8 or higher** installed on your system.
2. **MySQL Server (5.7 or 8.0+)** installed and running locally or remotely.

---

## 🚀 Step-by-Step Installation & Setup

### 1. Clone or Download the Project
```bash
git clone https://github.com/your-username/CineData-Analytics-Platform.git
cd CineData-Analytics-Platform
```

### 2. Set Up a Python Virtual Environment
**On Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up the MySQL Database (`movies_bookig_db`)

If you do not already have the database created on your MySQL server, import the provided `movies_bookig_db.sql` file using the MySQL CLI or MySQL Workbench:

**Using MySQL CLI:**
```bash
mysql -u root -p < movies_bookig_db.sql
```

**Using MySQL Workbench:**
1. Open MySQL Workbench and connect to your MySQL instance.
2. Go to **File** > **Open SQL Script...** and select `movies_bookig_db.sql`.
3. Click the **Execute (⚡)** button to create the database and tables.

---

## 💻 Running the Application

Launch the Streamlit web application:

```bash
python -m streamlit run app.py
```

Streamlit will automatically open your default browser at:
```
http://localhost:8501
```

---

## 📖 User Guide

### 1. Connecting to MySQL
1. In the left sidebar under **MySQL Connection**:
   - **Host**: Enter your MySQL host (default: `localhost`).
   - **Port**: Enter your MySQL port (default: `3306`).
   - **Username**: Enter your MySQL user (default: `root`).
   - **Password**: Enter your MySQL password.
   - **Database Name**: Automatically set to `movies_bookig_db`.
2. Click **Connect to MySQL**.
3. Upon a successful connection, a green indicator will appear and the discovered tables will be listed.

### 2. Exploring Database Tables
- Go to the **Database Tables Explorer** section.
- Select any table (`bookings`, `customers`, `movies`, `screens`, `theatres`) from the dropdown.
- The system will dynamically display the column names, data types, nullability, and primary/foreign key flags directly from MySQL `information_schema`.

### 3. Writing and Running SQL Queries
- Use the **SQL Query Editor** to write custom analytical queries.
- Click **Preset SQL Query Templates** to load sample queries.
- Click **▶ Run Query** to execute.

#### 💡 Example Queries to Try:

**Top 5 Rated Movies:**
```sql
SELECT title, genre, rating, language, release_date 
FROM movies 
ORDER BY rating DESC 
LIMIT 5;
```

**Total Revenue & Ticket Sales by Movie:**
```sql
SELECT 
    m.title, 
    COUNT(b.booking_id) AS total_bookings, 
    SUM(b.seats_booked) AS total_tickets_sold, 
    SUM(b.total_amount) AS total_revenue 
FROM movies m 
LEFT JOIN bookings b ON m.movie_id = b.movie_id 
GROUP BY m.movie_id, m.title 
ORDER BY total_revenue DESC;
```

**Screen Capacity Across Theatres:**
```sql
SELECT 
    s.screen_name, 
    s.screen_type, 
    s.seating_capacity, 
    t.theatre_name, 
    t.city 
FROM screens s 
JOIN theatres t ON s.theatre_id = t.theatre_id 
ORDER BY s.seating_capacity DESC;
```

**Customer Spend Summary:**
```sql
SELECT 
    c.customer_id, 
    c.full_name, 
    c.city, 
    COUNT(b.booking_id) AS total_bookings, 
    COALESCE(SUM(b.total_amount), 0) AS total_spent 
FROM customers c 
LEFT JOIN bookings b ON c.customer_id = b.customer_id 
GROUP BY c.customer_id, c.full_name, c.city 
ORDER BY total_spent DESC;
```

### 4. Exporting Results
- In the **Query Results** section, your query output is rendered in a responsive data table with row counts and execution timing.
- Click **📄 Download CSV** to export the current query result as a `.csv` file.
- Click **📊 Download Excel** to export the current query result as a `.xlsx` spreadsheet.
- *Note: Only the data from your executed query is exported, never the entire database.*

---

## 🛡️ Security and Validation Features

1. **Read-Only Enforcement**: The query executor only allows `SELECT`, `WITH`, `EXPLAIN`, `SHOW`, `DESCRIBE`, and `DESC`.
2. **Blocked Statements**: Statements containing `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `REPLACE`, `GRANT`, `REVOKE`, `CALL`, `EXEC`, or `EXECUTE` are intercepted and rejected with a friendly safety alert.
3. **Multi-Statement Prevention**: Chained semicolon-separated queries (e.g., `SELECT * FROM movies; DROP TABLE movies;`) are blocked before reaching MySQL.
4. **Isolated Metadata Scope**: Metadata discovery queries are strictly parameterized with `table_schema = DATABASE()`, ensuring other databases on the server are never exposed.

---

## 📤 Uploading to GitHub

To upload this project to your GitHub repository:

```bash
# 1. Initialize git (if not already initialized)
git init

# 2. Add all project files
git add .

# 3. Commit changes
git commit -m "Initial commit: CineData Analytics Platform"

# 4. Link to your GitHub remote repository
git branch -M main
git remote add origin https://github.com/your-username/CineData-Analytics-Platform.git

# 5. Push to GitHub
git push -u origin main
```

*(The included `.gitignore` ensures that virtual environments, cache files, and credentials are never pushed.)*

---

## 🔮 Future Scope
- Visual analytics and interactive charts (revenue trends, genre distribution).
- Saved query history and bookmarks.
- Natural Language to SQL query generation using LLM integration.
- Multi-user role management and granular query logging.

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
