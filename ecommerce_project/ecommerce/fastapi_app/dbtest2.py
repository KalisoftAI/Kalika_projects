import psycopg2
import os
from datetime import datetime
from tabulate import tabulate
import pandas as pd  # Added pandas

# Database connection parameters - same as before
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "ecom_prod_catalog")
db_user = os.getenv("DB_USER", "vikas")
db_password = os.getenv("DB_PASSWORD", "kalika1667")
db_port = os.getenv("DB_PORT", "5432")


def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        print("Database connected successfully.")
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def create_users_table():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return
        cursor = connection.cursor()
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

    except Exception as error:
        print(f"Error creating/ensuring 'users' table: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_orders_table():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS orders CASCADE;")
        connection.commit()
        print("Existing 'orders' table dropped (if it existed).")

        create_table_query = """
            CREATE TABLE orders (
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
        print("Table 'orders' created successfully.")

    except Exception as error:
        print(f"Error creating/ensuring 'orders' table: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_products_table():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS products CASCADE;")
        connection.commit()
        print("Existing 'products' table dropped.")

        create_table_query = '''
        CREATE TABLE products (
            action TEXT,
            item_id INTEGER PRIMARY KEY,
            main_category TEXT NOT NULL,
            sub_categories TEXT,
            item_code VARCHAR(50) UNIQUE NOT NULL,
            product_title TEXT NOT NULL,
            product_description TEXT,
            upc TEXT,
            brand TEXT,
            department TEXT,
            type TEXT,
            tag TEXT,
            list_price DECIMAL(10, 2),
            price DECIMAL(10, 2) NOT NULL,
            inventory BIGINT,
            min_order_qty BIGINT,
            available TEXT,
            large_image TEXT,
            additional_images TEXT,
            status VARCHAR(50) DEFAULT 'New',
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- Columns expanded from 'Item Properties'
            lead_time VARCHAR(255),
            length VARCHAR(255),
            material_type VARCHAR(255),
            sys_discount_group VARCHAR(255),
            sys_num_images VARCHAR(255),
            sys_product_type VARCHAR(255),
            unit_of_measure VARCHAR(255),
            unspsc VARCHAR(255)
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("New 'products' table created with expanded item properties.")

    except Exception as error:
        print(f"Error creating new 'products' table: {error}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def verify_table_schema(table_name):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return
        cursor = connection.cursor()
        print(f"\n--- Schema of '{table_name}' table ---")
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        schema = cursor.fetchall()
        if schema:
            print(tabulate(schema, headers=["Column Name", "Data Type", "Is Nullable"], tablefmt="grid"))
        else:
            print(f"Table '{table_name}' does not exist or has no columns.")
    except Exception as e:
        print(f"Error verifying schema for '{table_name}': {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def parse_item_properties(properties_string):
    properties_dict = {}
    if not properties_string or not isinstance(properties_string, str):
        return properties_dict

    parts = properties_string.split(',')
    for part in parts:
        if ' - ' in part:
            key, value = part.split(' - ', 1)
            clean_key = key.strip().lower().replace(' ', '_')
            properties_dict[clean_key] = value.strip()
    return properties_dict


def insert_data_from_excel(file_path):
    connection = None
    cursor = None
    try:
        # Read Excel file with pandas, all columns as string initially
        df = pd.read_excel(file_path, dtype=str)

        # Clean column names for consistency
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Connect to database
        connection = get_db_connection()
        if not connection:
            return
        cursor = connection.cursor()

        db_columns = [
            "item_id", "action", "main_category", "sub_categories", "item_code",
            "product_title", "product_description", "upc", "brand", "department",
            "type", "tag", "list_price", "price", "inventory", "min_order_qty",
            "available", "large_image", "additional_images", "status", "last_modified",
            "lead_time", "length", "material_type", "sys_discount_group", "sys_num_images",
            "sys_product_type", "unit_of_measure", "unspsc"
        ]

        placeholders = ', '.join(['%s'] * len(db_columns))
        insert_query = f"INSERT INTO products ({', '.join(db_columns)}) VALUES ({placeholders})"

        for idx, row in df.iterrows():
            # Parse item_properties if present, else empty dict
            properties_dict = parse_item_properties(row.get('item_properties', '') or '')

            # Safely convert numeric fields (handle scientific notation)
            def parse_int_safe(val):
                try:
                    return int(float(val)) if val and val.strip() != '' else None
                except:
                    return None

            def parse_float_safe(val):
                try:
                    return float(val) if val and val.strip() != '' else None
                except:
                    return None

            data_to_insert = [
                parse_int_safe(row.get('item_id')),
                row.get('action'),
                row.get('main_category'),
                row.get('sub_categories'),
                row.get('item_code'),
                row.get('product_title'),
                row.get('product_description'),
                row.get('upc'),
                row.get('brand'),
                row.get('department'),
                row.get('type'),
                row.get('tag'),
                parse_float_safe(row.get('list_price')),
                parse_float_safe(row.get('price')),
                parse_int_safe(row.get('inventory')),
                parse_int_safe(row.get('min_order_qty')),
                row.get('available'),
                row.get('large_image'),
                row.get('additional_images'),
                'New',  # default status
                datetime.now(),
                properties_dict.get('lead_time'),
                properties_dict.get('length'),
                properties_dict.get('material_type'),
                properties_dict.get('sys_discount_group'),
                properties_dict.get('sys_num_images'),
                properties_dict.get('sys_product_type'),
                properties_dict.get('unit_of_measure'),
                properties_dict.get('unspsc'),
            ]

            try:
                cursor.execute(insert_query, tuple(data_to_insert))
            except psycopg2.IntegrityError as ie:
                print(f"Skipping duplicate or invalid row with item_code {row.get('item_code')}: {ie}")
                connection.rollback()
            except Exception as e:
                print(f"Error inserting row with item_code {row.get('item_code')}: {e}")
                connection.rollback()

        connection.commit()
        print("Data insertion from Excel file completed.")

    except FileNotFoundError:
        print(f"Error: Excel file not found at '{file_path}'")
    except Exception as error:
        print(f"An error occurred: {error}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    excel_file_path = '/home/ubuntu/Kalika_projects/ecommerce_project/ecommerce/fastapi_app/filtered-products-new.xlsx'  # Update this path to your Excel file

    print("Attempting to create/ensure database tables...")
    create_users_table()

    create_products_table()
    verify_table_schema('products')

    create_orders_table()
    verify_table_schema('orders')

    print(f"\nAttempting to insert product data from Excel file: '{excel_file_path}'...")
    insert_data_from_excel(excel_file_path)

    # Final check of product count
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM products;")
            count = cursor.fetchone()[0]
            print(f"\nTotal products in database after insertion: {count}")
    except Exception as e:
        print(f"Error checking product count: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
