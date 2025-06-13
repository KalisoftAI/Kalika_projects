import secrets
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, send_from_directory, g, Response
from login import login1
from register import register1
from addtocart import add_cart
from checkout import check
from cart import cart1
from main import punchout
from flask_session import Session
from datetime import timedelta
import csv
from urllib.parse import quote
import logging
from logging.handlers import RotatingFileHandler
from flask_cors import CORS
import boto3
import redis

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create a logger specific to this module
logger = logging.getLogger("app")

# Initialize S3 client using environment variables for credentials and region
s3 = boto3.client('s3', region_name=os.getenv('AWS_DEFAULT_REGION'))

# Get S3 bucket and folder names from environment variables, with fallbacks
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'kalika-ecom')
FOLDER_NAME = os.getenv('S3_FOLDER_NAME', 'kalika-images/')

# Initialize logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Set to logging.INFO or logging.ERROR in production
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("app.log", maxBytes=5000000, backupCount=5),  # Logs to a file
        logging.StreamHandler()  # Logs to console
    ]
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key for Flask sessions

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize Flask-Session
Session(app)

# Register blueprints
app.register_blueprint(login1)
app.register_blueprint(register1)
app.register_blueprint(add_cart)
app.register_blueprint(check)
app.register_blueprint(cart1)
app.register_blueprint(punchout)

CORS(app) # Enable CORS for all routes by default

# Database connection parameters - moved from dbtest.py for completeness here
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'ecom_prod_catalog')
db_user = os.getenv('DB_USER', 'vikas')
db_password = os.getenv('DB_PASSWORD', 'your_password') # Use environment variable for password
db_port = os.getenv('DB_PORT', '5432')

# --- Database Connection Management (using Flask's g object) ---
def get_db_connection():
    """Establishes a new database connection or returns the existing one for the current request."""
    if 'db' not in g:
        try:
            g.db = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password,
                port=db_port
            )
            g.db.autocommit = False # Important for transactions
            logger.info("Database connection established successfully.")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            g.db = None # Indicate connection failed
    return g.db

def close_db_connection(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
        logger.info("Database connection closed during app teardown")

# Register the function to close the database connection when the app context tears down
app.teardown_appcontext(close_db_connection)

# --- Utility Functions for Database Interactions ---

def fetch_productcatalog_data():
    """Fetches product catalog data, mapping main categories to their subcategories."""
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to establish database connection in fetch_productcatalog_data()")
        return {} # Return empty dict on connection failure

    cursor = None
    try:
        cursor = connection.cursor()
        # FIX: Changed 'sub_category' to 'sub_categories' as per database hint
        cursor.execute("SELECT main_category, sub_categories FROM products;")
        rows = cursor.fetchall()
        category_data = {}
        for maincategory, subcategory in rows:
            if maincategory not in category_data:
                category_data[maincategory] = []
            if subcategory not in category_data[maincategory]:
                category_data[maincategory].append(subcategory)
        logger.debug(f"Categories fetched: {category_data}")
        return category_data
    except Exception as e:
        logger.error(f"Error fetching product catalog data: {e}")
        return {} # Return empty dict on error
    finally:
        if cursor:
            cursor.close() # Only close the cursor, connection is managed by app.teardown_appcontext

def fetch_categories():
    """
    Fetches distinct main categories from the database.
    Used for main category listings (e.g., carousel).
    """
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to establish database connection in fetch_categories()")
        return [] # Return empty list on connection failure

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT main_category FROM products WHERE main_category != 'Spring-\\xa0Air Hammer Drill Gun' LIMIT 12;")
        maincategories = cursor.fetchall()
        # Returns a list of dictionaries with category name and a placeholder image
        logger.debug(f"Main categories fetched: {[{'name': row[0], 'image': 'path/to/default/image.jpg'} for row in maincategories]}")
        return [{'name': row[0], 'image': 'path/to/default/image.jpg'} for row in maincategories]
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return [] # Return empty list on error
    finally:
        if cursor:
            cursor.close() # Only close the cursor, connection is managed by app.teardown_appcontext

def fetch_random_products(limit=8):
    """Fetches a limited number of random products for display on the home page."""
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to establish database connection in fetch_random_products()")
        return [] # Return empty list on connection failure

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT product_id, name, price, image_url FROM products ORDER BY RANDOM() LIMIT %s;", (limit,))
        products = cursor.fetchall()
        product_list = []
        for p_id, name, price, image_url in products:
            image_s3_url = get_s3_image_url(image_url) if image_url else 'path/to/default/product_image.jpg'
            product_list.append({
                'product_id': p_id,
                'name': name,
                'price': float(price),
                'image_url': image_s3_url
            })
        logger.debug(f"Random products fetched: {product_list}")
        return product_list
    except Exception as e:
        logger.error(f"Error fetching random products: {e}")
        return [] # Return empty list on error
    finally:
        if cursor:
            cursor.close() # Only close the cursor

def get_s3_image_url(image_name):
    """Generates a public URL for an image stored in S3."""
    if not image_name:
        return None
    try:
        # Construct the S3 key with the folder name
        s3_key = f"{FOLDER_NAME}{image_name}"
        # Generate a pre-signed URL for the object
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        return url
    except Exception as e:
        logger.error(f"Error generating S3 URL for {image_name}: {e}")
        return None

# --- Routes ---

@app.route('/')
def home():
    logger.info("Home page requested")
    try:
        main_categories_carousel = fetch_categories()
        product_catalog_data = fetch_productcatalog_data()
        random_products = fetch_random_products() # Call the function to fetch random products

        return render_template('index.html',
                               main_categories_carousel=main_categories_carousel,
                               category_data=product_catalog_data,
                               random_products=random_products)
    except Exception as e:
        logger.error(f"An error occurred in home(): {e}")
        # Returning a simple string response instead of rendering error.html
        return "An internal server error occurred. Please try again later.", 500


@app.route('/products/<main_category_name>')
def products_by_category(main_category_name):
    logger.info(f"Fetching products for category: {main_category_name}")
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            logger.error("Failed to establish database connection in products_by_category()")
            # Returning a simple string response instead of rendering error.html
            return "Database connection failed for products by category. Please try again later.", 500

        cursor = connection.cursor()
        # Decode the URL-encoded category name
        decoded_category_name = quote(main_category_name)

        # Fetch products for the given category
        cursor.execute("SELECT product_id, name, price, image_url, description FROM products WHERE main_category = %s;", (decoded_category_name,))
        products_raw = cursor.fetchall()

        products = []
        for p_id, name, price, image_url, description in products_raw:
            image_s3_url = get_s3_image_url(image_url) if image_url else '/static/default_product_image.jpg'
            products.append({
                'product_id': p_id,
                'name': name,
                'price': float(price),
                'image_url': image_s3_url,
                'description': description
            })

        main_categories_carousel = fetch_categories()
        product_catalog_data = fetch_productcatalog_data()

        return render_template('products.html',
                               main_category_name=main_category_name,
                               products=products,
                               main_categories_carousel=main_categories_carousel,
                               category_data=product_catalog_data)
    except Exception as e:
        logger.error(f"Error fetching products for category {main_category_name}: {e}")
        # Returning a simple string response instead of rendering error.html
        return "Failed to load products for this category. Please try again later.", 500
    finally:
        if cursor:
            cursor.close()


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    logger.info(f"Fetching details for product ID: {product_id}")
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            logger.error("Failed to establish database connection in product_detail()")
            # Returning a simple string response instead of rendering error.html
            return "Database connection failed for product details. Please try again later.", 500

        cursor = connection.cursor()
        cursor.execute("SELECT product_id, name, description, price, image_url, stock_quantity FROM products WHERE product_id = %s;", (product_id,))
        product_data = cursor.fetchone()

        if product_data:
            p_id, name, description, price, image_url, stock_quantity = product_data
            image_s3_url = get_s3_image_url(image_url) if image_url else '/static/default_product_image.jpg'
            product = {
                'product_id': p_id,
                'name': name,
                'description': description,
                'price': float(price),
                'image_url': image_s3_url,
                'stock_quantity': stock_quantity
            }
            main_categories_carousel = fetch_categories()
            product_catalog_data = fetch_productcatalog_data()
            return render_template('product_detail.html',
                                   product=product,
                                   main_categories_carousel=main_categories_carousel,
                                   category_data=product_catalog_data)
        else:
            # Returning a simple string response for product not found
            return "Product not found.", 404
    except Exception as e:
        logger.error(f"Error fetching product detail for ID {product_id}: {e}")
        # Returning a simple string response instead of rendering error.html
        return "Failed to load product details. Please try again later.", 500
    finally:
        if cursor:
            cursor.close()

@app.route('/search')
def search_products():
    query = request.args.get('query', '').strip()
    logger.info(f"Searching for products with query: {query}")
    products = []
    if query:
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            if connection is None:
                logger.error("Failed to establish database connection in search_products()")
                # Keeping flash message for client-side display on search results page
                flash("Database connection failed for search. Please try again.", "error")
                return render_template('search_results.html', query=query, products=[], main_categories_carousel=fetch_categories(), category_data=fetch_productcatalog_data())


            cursor = connection.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("SELECT product_id, name, price, image_url, description FROM products WHERE name ILIKE %s OR description ILIKE %s;", (search_pattern, search_pattern))
            products_raw = cursor.fetchall()

            for p_id, name, price, image_url, description in products_raw:
                image_s3_url = get_s3_image_url(image_url) if image_url else '/static/default_product_image.jpg'
                products.append({
                    'product_id': p_id,
                    'name': name,
                    'price': float(price),
                    'image_url': image_s3_url,
                    'description': description
                })
        except Exception as e:
            logger.error(f"Error during product search for query '{query}': {e}")
            flash("An error occurred during search. Please try again.", "error")
        finally:
            if cursor:
                cursor.close()

    main_categories_carousel = fetch_categories()
    product_catalog_data = fetch_productcatalog_data()
    return render_template('search_results.html',
                           query=query,
                           products=products,
                           main_categories_carousel=main_categories_carousel,
                           category_data=product_catalog_data)

@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(app.static_folder, 'robots.txt')


if __name__ == "__main__":
    logger.info("Starting the Flask application...")
    logger.info("Running the application in debug mode")
    app.run(host='0.0.0.0', port=5000, debug=True)