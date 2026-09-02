"""
Sample Database Generator for SQL Query Explorer.
Creates a realistic SQLite database in data/database.db
with sample tables: employees, departments, customers, orders, and products.
"""
import os
import sqlite3

def create_sample_database(db_path: str = "data/database.db") -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(50) NOT NULL,
            salary DECIMAL(10, 2) NOT NULL,
            hire_date DATE NOT NULL,
            city VARCHAR(50) NOT NULL
        )
    """)
    
    # Check if table already has rows
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        employees_data = [
            ("Alice Johnson", "Engineering", 85000.00, "2021-03-15", "San Francisco"),
            ("Bob Smith", "Engineering", 92000.00, "2020-07-01", "Seattle"),
            ("Charlie Brown", "Marketing", 48000.00, "2022-01-10", "New York"),
            ("Diana Prince", "Sales", 62000.00, "2019-11-20", "Chicago"),
            ("Evan Wright", "HR", 45000.00, "2023-02-01", "Austin"),
            ("Fiona Gallagher", "Engineering", 78000.00, "2021-09-18", "Denver"),
            ("George Clark", "Sales", 55000.00, "2020-04-12", "Boston"),
            ("Hannah Abbott", "Marketing", 51000.00, "2022-08-05", "San Francisco"),
            ("Ian Malcolm", "Research", 105000.00, "2018-06-30", "Seattle"),
            ("Julia Roberts", "HR", 52000.00, "2021-12-01", "New York"),
            ("Kevin Bacon", "Sales", 47000.00, "2023-04-15", "Atlanta"),
            ("Laura Croft", "Engineering", 98000.00, "2019-05-10", "San Francisco"),
            ("Michael Scott", "Sales", 65000.00, "2017-03-01", "Scranton"),
            ("Nina Simone", "Design", 58000.00, "2022-06-15", "Los Angeles"),
            ("Oscar Martinez", "Finance", 72000.00, "2019-08-22", "Scranton"),
            ("Pam Beesly", "Design", 46000.00, "2020-10-12", "Scranton"),
            ("Quinn Fabray", "Marketing", 53000.00, "2022-11-01", "Chicago"),
            ("Ryan Howard", "Research", 61000.00, "2021-01-20", "New York"),
            ("Sarah Connor", "Security", 89000.00, "2018-09-09", "Los Angeles"),
            ("Tom Holland", "Engineering", 74000.00, "2023-05-10", "Austin"),
            ("Uma Thurman", "Finance", 81000.00, "2020-02-14", "New York"),
            ("Victor Stone", "Engineering", 95000.00, "2019-12-03", "Seattle"),
            ("Wanda Maximoff", "Research", 110000.00, "2018-04-17", "Boston"),
            ("Xavier Charles", "Management", 125000.00, "2016-01-05", "New York"),
            ("Yvonne Strahovski", "Security", 77000.00, "2021-07-25", "San Francisco"),
            ("Zack Taylor", "Sales", 49000.00, "2023-08-01", "Chicago")
        ]
        cursor.executemany(
            "INSERT INTO employees (name, department, salary, hire_date, city) VALUES (?, ?, ?, ?, ?)",
            employees_data
        )
    
    # 2. Departments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name VARCHAR(50) NOT NULL UNIQUE,
            budget DECIMAL(12, 2) NOT NULL,
            location VARCHAR(50) NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM departments")
    if cursor.fetchone()[0] == 0:
        dept_data = [
            ("Engineering", 1500000.00, "Building A - Floor 3"),
            ("Marketing", 600000.00, "Building B - Floor 2"),
            ("Sales", 900000.00, "Building B - Floor 1"),
            ("HR", 350000.00, "Building A - Floor 1"),
            ("Finance", 750000.00, "Building A - Floor 2"),
            ("Research", 1200000.00, "Building C - Lab 1"),
            ("Security", 400000.00, "Building A - Ground"),
            ("Design", 500000.00, "Building C - Studio")
        ]
        cursor.executemany(
            "INSERT INTO departments (dept_name, budget, location) VALUES (?, ?, ?)",
            dept_data
        )
        
    # 3. Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            country VARCHAR(50) NOT NULL,
            signup_date DATE NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        cust_data = [
            ("Acme Corp", "contact@acme.com", "USA", "2022-01-15"),
            ("Globex Inc", "info@globex.org", "Canada", "2022-03-20"),
            ("Soylent Corp", "sales@soylent.com", "UK", "2022-06-10"),
            ("Initech LLC", "peter@initech.com", "USA", "2023-01-05"),
            ("Umbrella Corp", "support@umbrella.bio", "Germany", "2023-02-18"),
            ("Stark Industries", "tony@stark.io", "USA", "2021-11-12"),
            ("Wayne Enterprises", "bruce@wayne.com", "USA", "2021-08-30"),
            ("Cyberdyne Systems", "miles@cyberdyne.net", "Japan", "2023-07-22")
        ]
        cursor.executemany(
            "INSERT INTO customers (name, email, country, signup_date) VALUES (?, ?, ?, ?)",
            cust_data
        )

    # 4. Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock_quantity INTEGER NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        prod_data = [
            ("Cloud Database Enterprise", "Software", 499.99, 100),
            ("Analytics Suite Pro", "Software", 299.99, 250),
            ("Security Gateway Appliance", "Hardware", 1299.00, 45),
            ("Server Rack 42U", "Hardware", 850.00, 20),
            ("API Connector License", "Software", 99.00, 500),
            ("Support Tier 1 (Annual)", "Services", 1200.00, 80),
            ("Support Tier 2 24/7 (Annual)", "Services", 3500.00, 30),
            ("Ethernet Switch 48-Port", "Hardware", 450.00, 60)
        ]
        cursor.executemany(
            "INSERT INTO products (product_name, category, price, stock_quantity) VALUES (?, ?, ?, ?)",
            prod_data
        )

    # 5. Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            total_amount DECIMAL(10, 2) NOT NULL,
            status VARCHAR(20) NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        order_data = [
            (1, "2023-08-01", 1499.97, "Completed"),
            (2, "2023-08-05", 299.99, "Completed"),
            (3, "2023-08-12", 4799.00, "Processing"),
            (1, "2023-08-15", 850.00, "Completed"),
            (6, "2023-08-20", 5200.00, "Completed"),
            (7, "2023-08-22", 1299.00, "Shipped"),
            (4, "2023-08-25", 99.00, "Completed"),
            (5, "2023-08-28", 3500.00, "Pending"),
            (8, "2023-09-01", 450.00, "Completed")
        ]
        cursor.executemany(
            "INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (?, ?, ?, ?)",
            order_data
        )

    conn.commit()
    conn.close()
    print(f"Sample database created successfully at: {db_path}")

if __name__ == "__main__":
    create_sample_database()
