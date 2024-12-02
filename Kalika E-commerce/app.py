# from punchout import *
import secrets
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, send_from_directory
from login import login1
from register import register1
from addtocart import add_cart
from checkout import check
from products import products1
from cart import cart1
from main import punchout
from flask_session import Session
from datetime import timedelta
from db import get_db_connection
import csv
from urllib.parse import quote
import logging
from flask_cors import CORS


from db import get_db_connection

from flask_session import Session

# Initialize the Flask application
app = Flask(__name__, static_folder='static')
CORS(app)


# Flask Session Configuration
app.secret_key = secrets.token_hex(16)  # Generates a random 32-character hex string
app.config['SESSION_TYPE'] = 'filesystem'  # Store session data on the filesystem
app.config['SESSION_PERMANENT'] = False  # Make sessions non-permanent by default
app.config['SESSION_USE_SIGNER'] = True  # Sign the session ID for added security
app.config['SESSION_COOKIE_SECURE'] = True  # Use HTTPS for cookies in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Mitigate CSRF attacks
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Session expiration time
Session(app)



app.register_blueprint(login1)
app.register_blueprint(register1)
app.register_blueprint(add_cart)
app.register_blueprint(check)
app.register_blueprint(products1)
app.register_blueprint(cart1)
app.register_blueprint(punchout)


# # Set a random secret key for session management
# app.secret_key = secrets.token_hex(16)  # Generates a random 32-character hex string


def get_shared_data():
    return {
        "categories": fetch_productcatalog_data()
    }

@app.route('/')
def home():
    # Fetch main categories and categories for other sections
    maincategory = fetch_categories()  # For the carousel
    categories = fetch_productcatalog_data()  # For category-subcategory mapping

    # Fetch random products from the database
    random_products_query = """
        SELECT itemcode AS product_id, 
               productname AS product_name, 
               subcategory AS product_description, 
               price AS product_price, 
               productdescription AS product_image
        FROM productcatalog
        ORDER BY RANDOM()
        LIMIT 4;
    """

    # Fetch data using the connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(random_products_query)

    # Fetch column names
    column_names = [desc[0] for desc in cur.description]

    # Convert tuples to dictionaries
    random_products = [dict(zip(column_names, row)) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template(
        'index.html', 
        maincategory=maincategory,
        categories=categories,
        random_products=random_products
    )

# def dashboard():
#     print("user",session)
#     if 'user_id' in session:
#         return f"Welcome back, {session['user_email']}!"
#     return redirect(url_for('login1.login'))


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/privacypolicy')
def privacy():
    return render_template('privacy.html')

@app.route('/termsofservices')
def termsofservices():
    return render_template('terms.html')

@app.route('/faqs')
def faqs():
    return render_template('faq.html')


# @app.route('/dashboard')
# def dashboard():
#     print("user",session)
#     if 'user_id' in session:
#         return f"Welcome back, {session['user_email']}!"
#     return redirect(url_for('login1.login'))




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
    print("results:", result[1])
    cur.close()

    if result:
        return jsonify({
            "itemcode": result[0],
            "name": result[1],
            "subcategory": result[2],
            "price": result[3],
            "description": result[4]
        })
    else:
        # logging.warning(f"Product not found for itemcode: {itemcode}")
        return jsonify({"error": "Product not found"}), 404

# Route to display products by category
# @app.route('/<string:maincategory>')
# def show_category_products(maincategory):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     # Fetch products by category
#     query = """
#         SELECT itemcode, productname, subcategory, price
#         FROM productcatalog
#         WHERE maincategory = %s;
#     """
#     cursor.execute(query, (maincategory,))
#     productcatalog = cursor.fetchall()
#
#     # Convert fetched data to a list of dictionaries
#     product_list = [
#         {'itemcode': row[0], 'productname': row[1], 'subcategory': row[2], 'price': row[3]}
#         for row in productcatalog
#     ]
#     # print
#
#     cursor.close()
#     conn.close()
#
#     # Render the HTML template with fetched products
#     return render_template('category.html',
#                            maincategory=maincategory,
#                            products=product_list)

# Route to display products by category
# @app.route('/<string:maincategory>')
# def show_category_products(maincategory):
#     product_list = []

#     # Read products from the CSV file
#     with open('imagedata1.csv', mode='r', encoding='utf-8') as csvfile:
#         csv_reader = csv.DictReader(csvfile)
#         # Skip the first row
#         # next(csv_reader, None)

#         for row in csv_reader:
#             # Filter products by main category
#             if row['Main Category'] == maincategory:
#                 product_list.append({
#                     'itemcode': row['Item Code'],
#                     'productname': row['Product Title'],
#                     'subcategory': row['Sub Categories'],
#                     'price': float(row['Price']),
#                     'image_url': url_for('static', filename=f'images/{row["Large Image"]}')

#                 })

#     # print("Product details:", product_list)

#     # Render the HTML template with fetched products
#     return render_template('category.html',
#                            maincategory=maincategory,
#                            products=product_list)

@app.route('/<string:maincategory>')
def show_category_products(maincategory):
    conn = get_db_connection()
    categories = fetch_productcatalog_data()
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
        {'itemcode': row[0],'productname': row[1], 'subcategory': row[2], 'price': row[3]}
        for row in productcatalog
    ]
    #print

    cursor.close()
    conn.close()

    # Render the HTML template with fetched products
    return render_template('category.html', 
                           maincategory=maincategory, 
                           categories=categories,
                           products=product_list)




# Route to display products by subcategory
@app.route('/<string:maincategory>/<string:subcategory>')
def show_products(maincategory, subcategory):
    conn = get_db_connection()
    categories = fetch_productcatalog_data()
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
                           categories=categories,
                           products=product_list)


# Close the database connection on app teardown
@app.teardown_appcontext
def close_connection(exception):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.close()
    connection.close()


def fetch_productcatalog_data():
    """Fetch maincategory and subcategory data from the database."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT maincategory, subcategory
            FROM productcatalog LIMIT 15;
        """)
        rows = cursor.fetchall()

        # Create a dictionary mapping main categories to their subcategories
        category_data = {}
        for maincategory, subcategory in rows:
            if maincategory not in category_data:
                category_data[maincategory] = []
            if subcategory not in category_data[maincategory]:
                category_data[maincategory].append(subcategory)

        cursor.close()
        connection.close()

        return category_data
    except Exception as e:
        print(f"Error fetching product catalog data: {e}")
        return {}

# Example usage
categories = fetch_productcatalog_data()
# print(categories)

def fetch_categories():
    """Fetch categories from the database."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT maincategory FROM productcatalog WHERE maincategory != 'Spring-\xa0Air Hammer Drill Gun' LIMIT 12;")
        maincategories = cursor.fetchall()  # Fetch only the main categories
        print("maincategories", maincategories)
        cursor.close()
        connection.close()

        # Add a default image for each category
        return [{'name': row[0], 'image': 'path/to/default/image.jpg'} for row in maincategories]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

if __name__ == "__main__":
    app.run(debug=True)

