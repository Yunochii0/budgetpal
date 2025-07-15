import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('budget.db')
        return conn
    except Error as e:
        print(e)
    return conn

def create_all_tables(conn):
    """Create all necessary tables if they don't exist."""
    sql_statements = [
        """ CREATE TABLE IF NOT EXISTS expenses (
                id integer PRIMARY KEY,
                amount real NOT NULL,
                category text NOT NULL,
                date text NOT NULL,
                time text NOT NULL
            ); """,
        """ CREATE TABLE IF NOT EXISTS income (
                id integer PRIMARY KEY,
                amount real NOT NULL,
                source text NOT NULL,
                date text NOT NULL,
                notes text
            ); """,
        """ CREATE TABLE IF NOT EXISTS budgets (
                id integer PRIMARY KEY,
                name text NOT NULL,
                amount real NOT NULL,
                date text NOT NULL
            ); """,
        """ CREATE TABLE IF NOT EXISTS savings_goals (
                id integer PRIMARY KEY,
                goal text NOT NULL,
                date text NOT NULL
            ); """
    ]
    try:
        c = conn.cursor()
        for statement in sql_statements:
            c.execute(statement)
    except Error as e:
        print(e)

def reset_database(conn):
    """Deletes all records from all tables."""
    tables = ["expenses", "income", "budgets", "savings_goals"]
    try:
        cur = conn.cursor()
        for table in tables:
            cur.execute(f"DELETE FROM {table}")
        conn.commit()
        print("Database has been reset.")
    except Error as e:
        print(f"Error resetting database: {e}")


# --- Expense Functions ---
def add_expense(conn, expense):
    sql = ''' INSERT INTO expenses(amount,category,date,time) VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, expense)
    conn.commit()
    return cur.lastrowid

def get_all_expenses(conn):
    cur = conn.cursor()
    cur.execute("SELECT amount, date, time, category FROM expenses ORDER BY date DESC")
    return cur.fetchall()

def get_total_expenses(conn):
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM expenses")
    total = cur.fetchone()[0]
    return total if total else 0

# --- Income Functions ---
def add_income(conn, income_record):
    sql = ''' INSERT INTO income(amount,source,date,notes) VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, income_record)
    conn.commit()
    return cur.lastrowid

def get_all_income(conn):
    cur = conn.cursor()
    cur.execute("SELECT date, source, amount, notes FROM income ORDER BY date DESC")
    return cur.fetchall()
    
def get_latest_income(conn):
    cur = conn.cursor()
    cur.execute("SELECT date, source, amount FROM income ORDER BY id DESC LIMIT 1")
    return cur.fetchone()

def get_total_income(conn):
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM income")
    total = cur.fetchone()[0]
    return total if total else 0

# --- Budget Functions ---
def add_budget(conn, budget):
    sql = ''' INSERT INTO budgets(name, amount, date) VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, budget)
    conn.commit()
    return cur.lastrowid

def get_all_budgets(conn):
    cur = conn.cursor()
    cur.execute("SELECT name, amount FROM budgets ORDER BY date DESC")
    return cur.fetchall()

# --- Savings Functions ---
def add_saving_goal(conn, goal):
    sql = ''' INSERT INTO savings_goals(goal, date) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, goal)
    conn.commit()
    return cur.lastrowid

def get_all_savings_goals(conn):
    cur = conn.cursor()
    cur.execute("SELECT goal, date FROM savings_goals ORDER BY date DESC")
    return cur.fetchall()

# --- History Function ---
def get_all_transactions(conn):
    """Gets a combined list of income and expenses for the history page."""
    sql = """
        SELECT date, source AS description, amount, 'Income' AS type FROM income
        UNION ALL
        SELECT date, category AS description, amount, 'Expense' AS type FROM expenses
        ORDER BY date DESC
    """
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

# Add this function to your existing database.py

def delete_all_records(conn):
    """Delete all records from all tables."""
    tables = ['expenses', 'income', 'budgets', 'savings_goals']
    sql = "DELETE FROM {}"
    try:
        cur = conn.cursor()
        for table in tables:
            cur.execute(sql.format(table))
        conn.commit()
        print("All records have been deleted.")
    except Error as e:
        print(f"Error while deleting records: {e}")
        

# Add this function to your existing database.py

def get_expenses_by_category(conn):
    """Query expenses and group them by category for the pie chart."""
    sql = "SELECT category, SUM(amount) FROM expenses GROUP BY category"
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    except Exception as e:
        print(f"Error fetching expenses by category: {e}")
        return []
    
    # Add these two functions to your existing database.py

def get_recent_expenses(conn, limit=2):
    """Fetch the most recent expenses."""
    sql = "SELECT category, amount FROM expenses ORDER BY id DESC LIMIT ?"
    try:
        cur = conn.cursor()
        cur.execute(sql, (limit,))
        return cur.fetchall()
    except Exception as e:
        print(f"Error fetching recent expenses: {e}")
        return []

def get_recent_savings(conn, limit=2):
    """Fetch the most recent savings goals."""
    sql = "SELECT goal FROM savings_goals ORDER BY id DESC LIMIT ?"
    try:
        cur = conn.cursor()
        cur.execute(sql, (limit,))
        return cur.fetchall()
    except Exception as e:
        print(f"Error fetching recent savings: {e}")
        return []
    
    # Add this function to your existing database.py

def get_top_expenses(conn, limit=5):
    """Fetches the top N expenses by amount."""
    sql = "SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC LIMIT ?"
    try:
        cur = conn.cursor()
        cur.execute(sql, (limit,))
        return cur.fetchall()
    except Exception as e:
        print(f"Error fetching top expenses: {e}")
        return []
    