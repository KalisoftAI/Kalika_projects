import psycopg2
import csv
from datetime import datetime

# Database connection parameters
db_host = "localhost" # Change to your database host if not local
db_name = 'ecom_prod_catalog'
db_user = 'vikas'
db_password = 'kalika1667'
# db_password = 'kalika1992'

db_port = '5432' # Default PostgreSQL port

def create_users_table():
    connection = None # Initialize to None
    cursor = None     # Initialize to None
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        cursor = connection.cursor()

        # Corrected: Use CREATE TABLE IF NOT EXISTS
        create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'users' ensured to exist (or created).")

        # Optional: Insert a sample user after table creation (if it doesn't exist)
        # This INSERT should be part of a separate seeding function, not table creation
        # For demonstration, keeping it commented out to avoid repeated inserts on rerun
        # insert_sample_user_query = """
        #     INSERT INTO users (username, email, password_hash)
        #     VALUES ('john_doe1', 'john.doe1@example.com', 'hashed_password_1234')
        #     ON CONFLICT (email) DO NOTHING;
        # """
        # cursor.execute(insert_sample_user_query)
        # connection.commit()
        # print("Sample user inserted (if not already present).")

    except Exception as error:
        print(f"Error creating/ensuring 'users' table: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def create_orders_table():
    connection = None # Initialize to None
    cursor = None     # Initialize to None
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        cursor = connection.cursor()

        # Corrected: Use CREATE TABLE IF NOT EXISTS based on previous discussion
        create_table_query = """
            CREATE TABLE IF NOT EXISTS Orders (
                order_id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'Pending',
                total_amount DECIMAL(10, 2) NOT NULL,
                shipping_address TEXT,
                payment_status VARCHAR(50) DEFAULT 'Unpaid',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'Orders' ensured to exist (or created).")

    except Exception as error:
        print(f"Error creating/ensuring 'Orders' table: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def create_products_table():
    connection = None # Initialize to None
    cursor = None     # Initialize to None
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        cursor = connection.cursor()

        # Corrected: The CREATE TABLE query was commented out and commit was misplaced
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS products (
            Item_id SERIAL PRIMARY KEY,
            Main_Category VARCHAR(100) NOT NULL,
            Sub_Categories VARCHAR(100),
            Item_Code VARCHAR(50) UNIQUE NOT NULL,
            Product_Title VARCHAR(255) NOT NULL,
            Product_Description TEXT,
            Price DECIMAL(10, 2) NOT NULL
        );
        '''
        cursor.execute(create_table_query)
        connection.commit() # Commit after creating the table
        print("Table 'products' ensured to exist (or created).")

    except Exception as error:
        print(f"Error creating/ensuring 'products' table: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Function to insert data into the Products table
def insert_data_from_csv(file_path):
    connection = None # Initialize to None
    cursor = None     # Initialize to None
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        cursor = connection.cursor()

        # Open the CSV file and read its content
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)

            # Iterate over each row in the CSV and insert it into the database
            for row in csv_reader:
                insert_query = '''
                INSERT INTO products (Item_id, Main_Category, Sub_Categories, Item_Code, Product_Title, Product_Description, Price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (Item_id) DO NOTHING;  -- Prevent duplicate Item_id entries
                '''
                data = (
                    int(row['Item_id']),
                    row['Main_Category'],
                    row['Sub_Categories'],
                    row['Item_Code'],
                    row['Product_Title'],
                    row['Product_Description'],
                    float(row['Price'])
                )

                # Execute the insert query
                cursor.execute(insert_query, data)

        # Commit the transaction after all rows are inserted
        connection.commit()
        print("Data inserted successfully into products table.")

    except Exception as error:
        print(f"Error inserting data: {error}")

    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_order(user_id, total_amount, status, shipping_address, payment_status):
    connection = None # Initialize to None
    cursor = None     # Initialize to None
    order_date = datetime.now()
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO Orders (user_id, order_date, total_amount, status, shipping_address, payment_status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING order_id;
        ''', (user_id, order_date, total_amount, status, shipping_address, payment_status, order_date, order_date))

        order_id = cursor.fetchone()[0]
        connection.commit()
        print(f"Order inserted successfully with order_id: {order_id}")

    except Exception as e:
        if connection: # Check if connection was established before trying to rollback
            connection.rollback()
        print("Error inserting order:", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    # Ensure the tables exist before trying to insert data
    print("Attempting to create/ensure database tables...")
    create_users_table()
    create_orders_table()
    create_products_table() # This was commented out, now it's active

    print("\nAttempting to insert product data from CSV...")
    csv_file_path = 'C:\Kalisoft_project\Kalika_projects\kalika_catalog_products.csv'
    insert_data_from_csv(csv_file_path)

    # Example usage for inserting an order (uncomment if you want to test)
    # print("\nAttempting to insert a sample order...")
    # try:
    #     insert_order(
    #         user_id=1, # Ensure a user with user_id=1 exists in your 'users' table
    #         total_amount=150.75,
    #         status="pending",
    #         shipping_address="1234 Elm St, Springfield, USA",
    #         payment_status="paid"
    #     )
    # except Exception as e:
    #     print(f"Failed to insert sample order: {e}")

