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
import logging

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


# Set a random secret key for session management
app.secret_key = secrets.token_hex(16)  # Generates a random 32-character hex string


@app.route('/')
def home():
    # return render_template('index.html')
    categories = fetch_productcatalog_data()
    return render_template('index.html', categories=categories)


@app.route('/search', methods=['GET'])
def search():
    term = request.args.get('q', '')  # Get the search term from query params
    if not term:
        return jsonify([])  # Return empty list if no search term is provided

    conn = get_db_connection()
    cur = conn.cursor()

    # Execute the SQL query to search for products matching the term
    cur.execute("""
        SELECT itemcode, productname, subcategory, price 
        FROM productcatalog 
        WHERE productname ILIKE %s
    """, (f"%{term}%",))  # Case-insensitive match
    results = cur.fetchall()
    # print("results:", results)

    cur.close()
    return jsonify([{
        "itemcode": row[0],
        "name": row[1],
        "subcategory": row[2],
        "price": row[3]
    } for row in results])


@app.route('/product/<itemcode>', methods=['GET'])
def get_product_details(itemcode):
    print("Fetching product details")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT itemcode, productname, subcategory, price, productdescription 
        FROM productcatalog 
        WHERE itemcode = %s
    """, (itemcode,))
    result = cur.fetchone()
    print("results:",result[0],itemcode)
    # cur.close()

    if result:
        # return jsonify({
        #     "itemcode": result[0],
        #     "name": result[1],
        #     "subcategory": result[2],
        #     "price": result[3],
        #     "description": result[4]
        # })
        return render_template('product.html',
                                   itemcode=result[0],
                                   name=result[1],
                                   subcategory=result[2],
                                   price=result[3],
                                   description=result[4])
    else:
        # logging.warning(f"Product not found for itemcode: {itemcode}")
        return jsonify({"error": "Product not found"}), 404

@app.route('/product/<string:itemcode>')
def get_product(itemcode):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch product details by item code
    query = """
        SELECT itemcode, productname AS name, productdescription AS description, price, subcategory 
        FROM productcatalog 
        WHERE itemcode = %s;
    """
    cursor.execute(query, (itemcode,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    if product:
        return jsonify({
            "itemcode": product[0],
            "name": product[1],
            "description": product[2],
            "price": str(product[3]),  # Ensure price is a string
            "subcategory": product[4]
        })
    else:
        return jsonify({"error": "Product not found"}), 404


# Route to display products by category
@app.route('/<string:maincategory>')
def show_category_products(maincategory):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch products by category
    query = """
        SELECT itemcode, productname, subcategory, price 
        FROM productcatalog 
        WHERE maincategory = %s;
    """
    cursor.execute(query, (maincategory,))
    productcatalog = cursor.fetchall()

    # Convert fetched data to a list of dictionaries
    product_list = [
        {'itemcode': row[0], 'productname': row[1], 'subcategory': row[2], 'price': row[3]}
        for row in productcatalog
    ]
    # print

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
        SELECT itemcode, productname, productdescription, price 
        FROM productcatalog 
        WHERE maincategory = %s AND subcategory = %s;
    """
    cursor.execute(query, (maincategory, subcategory))
    productcatalog = cursor.fetchall()

    # Convert fetched data to a list of dictionaries
    product_list = [
        {'itemcode': row[0], 'productname': row[1], 'productdescription': row[2], 'price': row[3]}
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


def fetch_productcatalog_data():
    try:
        # Connect to the PostgreSQL database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Query to fetch maincategory and subcategory data from productcatalog
        cursor.execute("""
            SELECT maincategory, subcategory
            FROM productcatalog LIMIT 15

        """)
        rows = cursor.fetchall()

        # Organize the data into a dictionary
        category_data = {}
        for maincategory, subcategory in rows:
            if maincategory not in category_data:
                category_data[maincategory] = []
            if subcategory not in category_data[maincategory]:
                category_data[maincategory].append(subcategory)

        # Close the database connection
        cursor.close()
        connection.close()

        return category_data

    except Exception as e:
        print(f"Error fetching product catalog data: {e}")
        return {}


# Example usage
categories = fetch_productcatalog_data()
# print(categories)
if __name__ == "__main__":
    app.run(debug=True)

