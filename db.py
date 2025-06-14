# db.py
import psycopg2
from tabulate import tabulate
from datetime import datetime
from flask import g  # Import Flask's global context object
import os
import logging

logger = logging.getLogger(__name__)

# --- Database connection parameters ---
# Using os.getenv to be more flexible, but keeping your defaults
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'ecom_prod_catalog')
db_user = os.getenv('DB_USER', 'vikas')
db_password = os.getenv('DB_PASSWORD', 'kalika1667')
db_port = os.getenv('DB_PORT', '5432')

# --- NEW FLASK-SAFE CONNECTION MANAGEMENT ---
def get_db_connection():
    """
    Establishes a new database connection for the current request or returns an existing one.
    Uses Flask's 'g' object for efficiency and safety.
    """
    if 'db' not in g:
        try:
            g.db = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password,
                port=db_port
            )
            g.db.autocommit = True
            logger.info("Database connection established for this request.")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            g.db = None
    return g.db

def close_db_connection(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
        logger.info("Database connection closed for this request.")


# --- YOUR EXISTING UTILITY FUNCTIONS (UNCHANGED) ---
# These will now use a temporary, direct connection for script execution.

def get_direct_db_connection():
    """A direct connection for running this file as a script."""
    try:
        connection = psycopg2.connect(
            host=db_host, database=db_name, user=db_user, password=db_password, port=db_port
        )
        return connection
    except Exception as e:
        print(f"Direct database connection error: {e}")
        return None

def view_tables_and_data():
    connection = None
    cursor = None
    try:
        connection = get_direct_db_connection()
        if not connection: return
        cursor = connection.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print("Tables in the database:")
        for table in tables:
            print(f"- {table[0]}")

        cursor.execute(f"SELECT * FROM users LIMIT 10")
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        print("\nData from table 'users':")
        print(tabulate(rows, headers=colnames, tablefmt="grid"))

    except Exception as e:
        print("Error:", e)
    finally:
        if cursor: cursor.close()
        if connection: connection.close()


def create_punchout_table():
    connection = None
    cursor = None
    try:
        connection = get_direct_db_connection()
        if not connection: return
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS punchout_responses (
            id SERIAL PRIMARY KEY,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'punchout_responses' created or already exists.")
    except Exception as e:
        print("Error while creating table:", e)
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# ... (Your other functions like insert_sample_data, insert_user_data, etc., can remain here,
#      just make sure they use get_direct_db_connection()) ...


# This allows you to run "python db.py" to use your admin functions
if __name__ == '__main__':
    view_tables_and_data()