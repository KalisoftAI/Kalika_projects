# from punchout import *
import secrets
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from psycopg2 import sql

from login import login1
from register import register1
from addtocart import add_cart
from checkout import check
from products import products1
from cart import cart1
# from home import home

from db import get_db_connection

from flask_session import Session

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # Store session data on the filesystem
Session(app)


app.register_blueprint(login1)
app.register_blueprint(register1)
app.register_blueprint(add_cart)
app.register_blueprint(check)
app.register_blueprint(products1)
app.register_blueprint(cart1)
# # app.register_blueprint(home)


# Set a random secret key for session management
app.secret_key = secrets.token_hex(16)  # Generates a random 32-character hex string

# Database connection parameters
# db_host = "3.108.190.220" 
# db_name = 'ecom_prod_catalog'
# db_user = 'vikas'
# db_password = 'kalika1667'

# connection = psycopg2.connect(
#             host=db_host,
#             database=db_name,
#             user=db_user,
#             password=db_password,
#             port='5432'
#         )
# cursor = connection.cursor()

# Connect to your PostgreSQL database
# def get_db_connection():
#     try:
#         connection = psycopg2.connect(
#             host=db_host,
#             database=db_name,
#             user=db_user,
#             password=db_password,
#             port='5432'
#         )
#         print("Database connected")
#         return connection
#     except Exception as e:
#         print(f"Database connection error: {e}")

# get_db_connection()


@app.route('/')
def home():
    return render_template('index.html')


# Close the database connection on app teardown
@app.teardown_appcontext
def close_connection(exception):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    app.run(debug=True)


# Route for Prouct page
