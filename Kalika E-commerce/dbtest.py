import psycopg2
import csv
from datetime import datetime

# Database connection parameters
db_host = "3.108.190.220" 
db_name = 'ecom_prod_catalog'
db_user = 'vikas'
db_password = 'kalika1667'

def create_users_table():
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port='5432'
        )
        cursor = connection.cursor()

        create_table_query = """
                            INSERT INTO users (username, email, password_hash)
                    VALUES
                    ('john_doe1', 'john.doe1@example.com', 'hashed_password_1234');
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'users' created successfully.")

    except Exception as error:
        print(f"Error creating table: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_orders_table():
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port='5432'
        )
        cursor = connection.cursor()

#         create_table_query = """
#                             CREATE TABLE Orders (
#     order_id INT PRIMARY KEY AUTO_INCREMENT,
#     user_id INT NOT NULL,
#     order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     status VARCHAR(50) DEFAULT 'Pending',
#     total_amount DECIMAL(10, 2) NOT NULL,
#     shipping_address TEXT,
#     FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
# );
#         """

        create_table_query=""" Select * from orders """
        cursor.execute(create_table_query)
        result=cursor.fetchall()
        print(result)
        connection.commit()
        print("Table 'users' created successfully.")

    except Exception as error:
        print(f"Error creating table: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_products_table():
    order_date = datetime.now()

    connection = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port='5432'
    )
    cursor = connection.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS Products (
    Item_id SERIAL PRIMARY KEY,
    Main_Category VARCHAR(100) NOT NULL,
    Sub_Categories VARCHAR(100),
    Item_Code VARCHAR(50) UNIQUE NOT NULL,
    Product_Title VARCHAR(255) NOT NULL,
    Product_Description TEXT,
    Price DECIMAL(10, 2) NOT NULL
    );
    '''
    
    
    
    connection.commit()
    # print(f"Order inserted successfully with order_id: {order_id}")

    # Close the database connection
    cursor.close()
    connection.close()


# Function to insert data into the Products table
def insert_data_from_csv(file_path):
    try:
        connection = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port='5432'
        )
        cursor = connection.cursor()
        
        # Open the CSV file and read its content
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            
            # Iterate over each row in the CSV and insert it into the database
            for row in csv_reader:
                insert_query = '''
                INSERT INTO Products (Item_id, Main_Category, Sub_Categories, Item_Code, Product_Title, Product_Description, Price)
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
                
        # Commit the transaction
        connection.commit()
        print("Data inserted successfully.")
        
    except Exception as error:
        print(f"Error inserting data: {error}")
    
    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()



def insert_order(user_id, total_amount, status, shipping_address, payment_status):
    order_date = datetime.now()
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port='5432'
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

        # Close the database connection
        cursor.close()
        connection.close()

    except Exception as e:
        connection.rollback()
        print("Error inserting order:", e)



if __name__ == "__main__":
    # create_users_table()
    # create_orders_table()
    # Example usage
    # insert_order(
    # user_id=1,                    # Assuming this user ID exists in the Users table
    # total_amount=150.75,
    # status="pending",
    # shipping_address="1234 Elm St, Springfield, USA",
    # payment_status="paid"
    # )

    # create_products_table()
    # Run the function to insert data from CSV
    csv_file_path= '../data/kalika_catalog_products.csv'
    insert_data_from_csv(csv_file_path)



