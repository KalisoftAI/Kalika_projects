import psycopg2

# Database connection parameters
# db_host = '35.154.205.144'  # or your server's IP address if remote
db_host = '15.206.157.168'
db_name = 'ecom_prod_catalog'
db_user = 'vikas'
db_password = 'kalika1667'

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

    # Execute a simple query
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record)

except Exception as error:
    print("Error while connecting to PostgreSQL", error)
# finally:
#     if connection:
#         cursor.close()
#         connection.close()
#         print("PostgreSQL connection is closed")