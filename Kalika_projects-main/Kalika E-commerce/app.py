# from punchout import *
import secrets
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, jsonify,  flash, session
from login import login1
from register import register1
from addtocart import add_cart
from checkout import check
from products import products1
from cart import cart1
# from home import home

from db import get_db_connection


app = Flask(__name__)


app.register_blueprint(login1)
app.register_blueprint(register1)
app.register_blueprint(add_cart)
app.register_blueprint(check)
app.register_blueprint(products1)
app.register_blueprint(cart1)
# # app.register_blueprint(home)


# Set a random secret key for session management
app.secret_key = secrets.token_hex(16)  # Generates a random 32-character hex string


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
#new app.py
