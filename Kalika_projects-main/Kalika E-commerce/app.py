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
from main import punchout
from punchoutsetup import punchout1
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
app.register_blueprint(punchout)
app.register_blueprint(punchout1)
# # app.register_blueprint(home)


# Set a random secret key for session management
app.secret_key = secrets.token_hex(16)  # Generates a random 32-character hex string


@app.route('/')
def home():
    return render_template('index.html')




# Route to display products by category
@app.route('/<string:maincategory>')
def show_category_products(maincategory):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch products by category
    query = """
        SELECT productname,  subcategory, price 
        FROM productcatalog 
        WHERE maincategory = %s;
    """
    cursor.execute(query, (maincategory,))
    productcatalog = cursor.fetchall()

    # Convert fetched data to a list of dictionaries
    product_list = [
        {'productname': row[0], ' subcategory': row[1], 'price': row[2]}
        for row in productcatalog
    ]
    

    cursor.close()
    conn.close()

    # Render the HTML template with fetched products
    return render_template('category.html', 
                           maincategory=maincategory, 
                           products=product_list)




# Route to display products by subcategory
@app.route('/<string:maincategory>/<string:subcategory>')
def show_products(maincategory, subcategory):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch products based on category and subcategory
    query = """
        SELECT productname, productdescription, price 
        FROM productcatalog 
        WHERE maincategory = %s AND subcategory = %s;
    """
    cursor.execute(query, (maincategory, subcategory))
    productcatalog = cursor.fetchall()

    # Convert fetched data to a list of dictionaries
    product_list = [
        {'productname': row[0], 'productdescription': row[1], 'price': row[2]}
        for row in productcatalog
    ]

    cursor.close()
    conn.close()

    # Render the HTML template with the fetched products
    return render_template('subcategory.html', 
                           maincategory=maincategory, 
                           subcategory=subcategory, 
                           products=product_list)



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
