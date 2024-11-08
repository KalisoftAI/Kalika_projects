import psycopg2
from tabulate import tabulate

# Database connection parameters
db_host = '3.108.190.220'
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

        # Execute a query to get table names
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")

        # Fetch all results
        tables = cursor.fetchall()

        # Print each table name
        for table in tables:
            print(table[0])

        # Query to fetch all rows in the orders table
        query = "SELECT * FROM orders;"

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Get column names for table structure
        colnames = [desc[0] for desc in cursor.description]

        # Display results in a table format
        print(tabulate(rows, headers=colnames, tablefmt="pretty"))

        # Print each row
        for row in rows:
            print(row)

        # Grant permissions on the public schema
        # cursor.execute("\c {db_name}")
        cursor.execute(f"GRANT USAGE ON SCHEMA public TO {db_user};")
        cursor.execute(f"GRANT CREATE ON SCHEMA public TO {db_user};")
        cursor.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO vikas;")

        connection.commit()
        print(f"Permissions granted to user '{db_user}' on public schema.")

    except Exception as error:
        print(f"Error creating permissions: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == '__main__':
    initialize_connection()
    # insert_users_data('john_doe', 'john@example.com')
    # create_orders_table()
