import psycopg2
from tabulate import tabulate
from datetime import datetime
from flask import g
# Database connection parameters
db_host = 'localhost'
db_name = 'ecom_prod_catalog'
db_user = 'vikas'
db_password = 'kalika1667'

# Connect to your PostgreSQL database
def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port='5432'
        )
        print("Database connected")
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")


def view_tables_and_data():

    try:
        # Connect to the PostgreSQL database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Query to get all table names
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
        """)

        # Fetch and display table names
        tables = cursor.fetchall()
        print("Tables in the database:")
        for table in tables:
            print(f"- {table[0]}")

        # Ask user for a table to view data
        # selected_table = input("\nEnter the punchout_responses to view its data: ")

        # Query to fetch data from the selected table
        cursor.execute(f"SELECT * FROM users")  # Limit for safety
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]  # Fetch column names

        # if rows:
        # print(f"\nData from table 'users':")
        print(tabulate(rows, headers=colnames, tablefmt="grid"))  # Tabular format
        # else:
        #     print(f"\nNo data found in table 'punchout_responses'.")

    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()



def create_punchout_table():
    # SQL commands to drop and create the table
    # drop_table_query = "DROP TABLE IF EXISTS punchout_responses;"
    create_table_query = """
    CREATE TABLE punchout_responses (
        id SERIAL PRIMARY KEY,
        response TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        # Connect to the PostgreSQL database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Drop the existing table if it exists
        # cursor.execute(drop_table_query)
        # print("Previous table 'punchout_responses' deleted successfully!")

        # Create a new table
        cursor.execute(create_table_query)
        connection.commit()
        print("New table 'punchout_responses' created successfully!")

    except Exception as e:
        print("Error while creating table:", e)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_sample_data():
    """
    Inserts sample data into the punchout_responses table.
    """
    # Sample XML data as a string
    sample_response = """<PunchOutSetupResponse>
        <Response>
            <Status code="200" text="OK" />
        </Response>
        <StartPage>
            <URL>https://example.com/punchout</URL>
        </StartPage>
    </PunchOutSetupResponse>"""

    # Connect to PostgreSQL
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to the database.")
        return

    try:
        cursor = connection.cursor()

        # Insert query
        insert_query = "INSERT INTO punchout_responses (response) VALUES (%s);"

        # Execute the query with the sample data
        cursor.execute(insert_query, (sample_response,))
        connection.commit()

        print("Sample data inserted successfully!")

    except Exception as e:
        print("Error while inserting sample data:", e)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Call the function
# insert_sample_data()


    

def insert_user_data(username, email):
    connection = None
    cursor = None
    try:
        # Establishing the connection
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port='5432'
        )
        cursor = connection.cursor()
        table="users2"
        # Insert new user data into users4 table
        cursor.execute(f"INSERT INTO {table} (username, email) VALUES (%s, %s);", (username, email))
        connection.commit()
        print(f"User data inserted: Username='{username}', Email='{email}'")

    except Exception as error:
        print(f"Error inserting data: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_orders_table():
    try:
        # Connect to your PostgreSQL database
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port='5432'
        )
        cursor = connection.cursor()

        # Create table query
        create_table_query = ''' CREATE TABLE orders (
                                order_id SERIAL PRIMARY KEY,                  -- Unique order ID
                                customer_id INT NOT NULL,                     -- Reference to the customer who placed the order
                                product_id INT NOT NULL,                      -- Reference to the product being ordered
                                quantity INT NOT NULL CHECK (quantity > 0),   -- Quantity of the product
                                price DECIMAL(10, 2) NOT NULL,                -- Price of the product at the time of order
                                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Date and time the order was placed
                                status VARCHAR(50) DEFAULT 'Pending',         -- Order status (e.g., 'Pending', 'Shipped', 'Delivered')
                                shipping_address TEXT,                        -- Shipping address for the order
                                payment_method VARCHAR(50),                   -- Payment method (e.g., 'Credit Card', 'PayPal')
                                payment_status VARCHAR(50) DEFAULT 'Unpaid',  -- Payment status (e.g., 'Paid', 'Unpaid')
                                shipping_date TIMESTAMP,                      -- Date the order was shipped
                                delivery_date TIMESTAMP,                      -- Date the order was delivered
                                CONSTRAINT fk_customer
                                    FOREIGN KEY (customer_id) 
                                    REFERENCES customers(customer_id),        -- Foreign key to customers table
                                CONSTRAINT fk_product
                                    FOREIGN KEY (product_id) 
                                    REFERENCES products(product_id)           -- Foreign key to products table
                            );
                            '''

        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'orders' created successfully.")

    except Exception as error:
        print(f"Error creating table: {error}")
    # finally:
    #     cursor.close()
    #     connection.close()


def initialize_connection():
        sample_order = {
        "user_id": 1,
        "order_date": datetime.now(),
        "total_amount": 150.75,
        "status": "Pending",
        "shipping_address": "1234 Elm Street, Springfield, IL",
        "payment_status": "Unpaid",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
        }

        # SQL query to insert data into the orders table
        insert_query = """
        INSERT INTO orders (user_id, order_date, total_amount, status, shipping_address, payment_status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING order_id;
        """

        # Connect to the PostgreSQL database
        cursor = connection.cursor()

        # Execute the insert query with the sample data
        cursor.execute(insert_query, (
            sample_order["user_id"],
            sample_order["order_date"],
            sample_order["total_amount"],
            sample_order["status"],
            sample_order["shipping_address"],
            sample_order["payment_status"],
            sample_order["created_at"],
            sample_order["updated_at"]
        ))

        # Fetch the returned order_id
        order_id = cursor.fetchone()[0]
        connection.commit()

        print(f"Order inserted successfully with order_id: {order_id}")

# This function will be registered with @app.teardown_appcontext in app.py
def close_db_connection(e=None):
    """Closes the database connection at the end of the request."""
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()
        print("Database connection closed")
    


if __name__ == '__main__':
    # insert_sample_data()
    # create_punchout_table()
    view_tables_and_data()
    # initialize_connection()
    # insert_users_data('john_doe', 'john@example.com')
    # create_orders_table()
    # create_punchout_table()
