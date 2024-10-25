import psycopg2

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

if __name__ == "__main__":
    create_users_table()
