import psycopg2
import csv
from datetime import datetime

# --- IMPORTANT: Update with your actual database credentials ---
DB_HOST = "localhost"
DB_NAME = 'ecom_prod_catalog'
DB_USER = 'vikas'
DB_PASSWORD = 'kalika1667'
DB_PORT = '5432'

def get_db_connection():
    """Establishes a connection to the database."""
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return connection
    except psycopg2.OperationalError as e:
        print(f"🔴 Could not connect to the database: {e}")
        return None

def create_products_table():
    """
    Creates the Products table with an image_url column.
    It first DROPS the table if it exists to ensure a fresh start.
    """
    connection = get_db_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            # Drop the old table to avoid conflicts with the new schema
            print("Dropping 'Products' table if it exists...")
            cursor.execute("DROP TABLE IF EXISTS Products;")

            # Create the table with the correct schema, including image_url
            create_table_query = '''
            CREATE TABLE Products (
                Item_id SERIAL PRIMARY KEY,
                Main_Category VARCHAR(255) NOT NULL,
                Sub_Categories VARCHAR(255),
                Item_Code VARCHAR(100) UNIQUE NOT NULL,
                Product_Title VARCHAR(255) NOT NULL,
                Product_Description TEXT,
                Price DECIMAL(10, 2) NOT NULL,
                image_url VARCHAR(255)  -- Added image_url column
            );
            '''
            print("Creating new 'Products' table...")
            cursor.execute(create_table_query)
            connection.commit()
            print("✅ Table 'Products' created successfully with 'image_url' column.")

    except Exception as error:
        print(f"❌ Error creating table: {error}")
    finally:
        if connection:
            connection.close()

def insert_data_from_csv(file_path):
    """
    Inserts product data from a CSV file into the Products table.
    Assumes the CSV has a header row matching the table columns, including 'image_url'.
    """
    connection = get_db_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                print("Inserting data from CSV...")

                for row in csv_reader:
                    # IMPORTANT: Your CSV needs these exact column names.
                    insert_query = '''
                    INSERT INTO Products (
                        Item_id, Main_Category, Sub_Categories, Item_Code,
                        Product_Title, Product_Description, Price, image_url
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (Item_Code) DO NOTHING;
                    '''
                    data = (
                        int(row['Item_id']),
                        row['Main_Category'],
                        row['Sub_Categories'],
                        row['Item_Code'],
                        row['Product_Title'],
                        row['Product_Description'],
                        float(row['Price']),
                        row['image_url']  # The new image_url field from CSV
                    )
                    cursor.execute(insert_query, data)

            connection.commit()
            print("✅ Data inserted successfully from CSV.")

    except (Exception, psycopg2.Error) as error:
        print(f"❌ Error inserting data: {error}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    # 1. Create the table with the correct schema
    create_products_table()

    # 2. Path to your CSV file
    csv_file_path = 'V:/ML_projects/Bussiness/Kalika_projects/kalika_catalog_products.csv'

    # 3. Insert data into the newly created table
    insert_data_from_csv(csv_file_path)