import psycopg2

# Database connection parameters
db_host = '15.206.157.168'
db_name = 'ecom_prod_catalog'
db_user = 'vikas'
db_password = 'kalika1667'


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
        create_table_query = ''' '''

        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'users' created successfully.")

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

        # Grant permissions on the public schema
        cursor.execute("\c {db_name}")
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