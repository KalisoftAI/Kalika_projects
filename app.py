# app.py (Updated and Corrected)

import secrets
import psycopg2
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, g, jsonify
)
from flask_session import Session
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import os
import boto3

# --- Import Blueprints and DB ---
from db import get_db_connection, close_db_connection
from login import login1
from register import register1
from cart import cart1

# --- Setup ---
load_dotenv()
logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# --- S3 CLIENT SETUP ---
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                  region_name=os.getenv('AWS_DEFAULT_REGION'))
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'kalika-ecom')
FOLDER_NAME = os.getenv('S3_FOLDER_NAME', 'kalika-images/')

# --- Session & Blueprint Configuration ---
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.teardown_appcontext(close_db_connection)

app.register_blueprint(login1)
app.register_blueprint(register1)
app.register_blueprint(cart1)

# --- Context Processor for Header ---
@app.context_processor
def inject_categories():
    full_catalog = fetch_productcatalog_data()
    limited_catalog = dict(list(full_catalog.items())[:10])
    return dict(categories=limited_catalog)

# --- Utility Functions with S3 Logic ---
def get_s3_image_url(image_name):
    if not image_name: return None
    try:
        s3_key = f"{FOLDER_NAME}{image_name.strip()}"
        return s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': s3_key}, ExpiresIn=3600)
    except Exception as e:
        logger.error(f"Error generating S3 URL for '{image_name}': {e}")
        return None

def fetch_productcatalog_data():
    connection = get_db_connection()
    if connection is None: return {}
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT main_category, sub_categories FROM products ORDER BY main_category;')
            category_data = {}
            for main, sub in cursor.fetchall():
                if main and main not in category_data: category_data[main] = []
                if main and sub and sub not in category_data[main]: category_data[main].append(sub)
            return category_data
    except Exception as e:
        logger.error(f"Error fetching product catalog data: {e}")
        return {}

def fetch_categories():
    connection = get_db_connection()
    if connection is None: return []
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT DISTINCT main_category FROM products WHERE main_category IS NOT NULL LIMIT 12;')
            return [{'name': row[0]} for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return []

def fetch_random_products(limit=8):
    connection = get_db_connection()
    if connection is None: return []
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT item_id, item_code, product_title, price, image_url, product_description FROM products ORDER BY RANDOM() LIMIT %s;',
                (limit,))
            product_list = []
            for p_id, item_code, name, price, image_url, desc in cursor.fetchall():
                final_image_url = get_s3_image_url(image_url) or url_for('static', filename='images/default.jpg')
                product_list.append({
                    'id': p_id,
                    'code': item_code,
                    'name': name,
                    'price': float(price or 0.0),
                    'image_url': final_image_url,
                    'description': desc
                })
            return product_list
    except Exception as e:
        logger.error(f"Error fetching random products: {e}")
        return []

# --- Page Rendering Routes ---
@app.route('/')
def home():
    return render_template('index.html',
                           maincategory=fetch_categories(),
                           random_products=fetch_random_products())

@app.route('/products/<main_category_name>')
def products_by_category(main_category_name):
    connection = get_db_connection()
    if connection is None: return redirect(url_for('home'))
    products = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT item_id, item_code, product_title, sub_categories, price, image_url FROM products WHERE main_category = %s;',
                (main_category_name,))
            for p_id, item_code, name, subcat, price, image_url in cursor.fetchall():
                final_image_url = get_s3_image_url(image_url) or url_for('static', filename='images/default.jpg')
                products.append({
                    "id": p_id,
                    "code": item_code,
                    "name": name,
                    "subcategory": subcat,
                    "price": float(price or 0.0),
                    "image_url": final_image_url
                })
        # Renders your product page for a main category
        # ⭐️ SUGGESTION: Changed 'cateogory.html' to 'product.html'
        return render_template('product.html', maincategory=main_category_name, products=products)
    except Exception as e:
        logger.error(f"Error fetching products for category {main_category_name}: {e}")
        return redirect(url_for('home'))


@app.route('/products/<main_category_name>/<sub_category_name>')
def products_by_subcategory(main_category_name, sub_category_name):
    connection = get_db_connection()
    if connection is None: return redirect(url_for('home'))
    products = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT item_id, item_code, product_title, price, image_url FROM products WHERE main_category = %s AND sub_categories = %s;',
                (main_category_name, sub_category_name))
            for p_id, item_code, name, price, image_url in cursor.fetchall():
                final_image_url = get_s3_image_url(image_url) or url_for('static', filename='images/default.jpg')
                products.append({
                    "id": p_id,
                    "code": item_code,
                    "name": name,
                    "price": float(price or 0.0),
                    "image_url": final_image_url
                })
        return render_template('subcategory.html', subcategory=sub_category_name, products=products)
    except Exception as e:
        logger.error(f"Error fetching products for subcategory {sub_category_name}: {e}")
        return redirect(url_for('home'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = None
    connection = get_db_connection()
    if connection is None:
        flash("Database error.", "error")
        return redirect(url_for('home'))
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT item_id, item_code, product_title, price, image_url, product_description FROM products WHERE item_id = %s;",
                (product_id,))
            p = cursor.fetchone()
            if p:
                final_image_url = get_s3_image_url(p[4]) or url_for('static', filename='images/default.jpg')
                product = {
                    'id': p[0],
                    'code': p[1],
                    'name': p[2],
                    'price': float(p[3] or 0.0),
                    'image_url': final_image_url,
                    'description': p[5]
                }
    except Exception as e:
        logger.error(f"Error fetching product detail for ID {product_id}: {e}")

    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for('home'))

    return render_template('product_detail.html', product=product)

@app.route('/search')
def search_products():
    query = request.args.get('query', '').strip()
    products = []
    if not query:
        return redirect(url_for('home'))

    connection = get_db_connection()
    if connection is None: return redirect(url_for('home'))
    try:
        with connection.cursor() as cursor:
            search_pattern = f"%{query}%"
            cursor.execute(
                "SELECT item_id, item_code, product_title, sub_categories, price, image_url, product_description FROM products WHERE product_title ILIKE %s OR product_description ILIKE %s;",
                (search_pattern, search_pattern))
            for p_id, item_code, name, subcat, price, image_url, desc in cursor.fetchall():
                final_image_url = get_s3_image_url(image_url) or url_for('static', filename='images/default.jpg')
                products.append({
                    "id": p_id,
                    "code": item_code,
                    "name": name,
                    "subcategory": subcat,
                    "price": float(price or 0.0),
                    "image_url": final_image_url,
                    "description": desc
                })
    except Exception as e:
        logger.error(f"Error during search for query '{query}': {e}")

    return render_template('search_results.html', query=query, products=products)

# --- Context Processors ---
@app.context_processor
def inject_categories():
    # ... (your existing category injection logic) ...
    full_catalog = fetch_productcatalog_data()
    limited_catalog = dict(list(full_catalog.items())[:10])
    return dict(categories=limited_catalog)

# ⭐ ADDED: Makes cart count available to all templates
@app.context_processor
def inject_cart_count():
    """Injects the total number of items in the cart into every template."""
    cart = session.get('cart', [])
    # Sum the quantity of all items in the cart
    cart_count = sum(item.get('quantity', 0) for item in cart)
    return dict(cart_count=cart_count)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)