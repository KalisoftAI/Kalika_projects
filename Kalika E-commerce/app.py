import secrets
import boto3
import redis
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, send_from_directory, g
from flask_session import Session
from flask_cors import CORS

# Import blueprints
from login import login1
from register import register1
from addtocart import add_cart
from checkout import check
from cart import cart1
from main import punchout

# Import database connection functions from db.py
from db import get_db_connection, close_db_connection

# Initialize logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("app.log", maxBytes=5000000, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- AWS S3 and Flask App Initialization ---
S3_BUCKET_NAME = 'kalikaecom'
S3_FOLDER_NAME = 'Folder/'
S3_REGION = 'ap-south-1'
s3 = boto3.client('s3', region_name=S3_REGION)

app = Flask(__name__, static_folder='static')
CORS(app)

# --- Session Configuration using Redis ---
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)
Session(app)

# Register blueprints for modular routes
app.register_blueprint(login1)
app.register_blueprint(register1)
app.register_blueprint(add_cart)
app.register_blueprint(check)
app.register_blueprint(cart1)
app.register_blueprint(punchout)


# --- Utility Functions ---

def generate_presigned_url(image_key):
    """Generates a pre-signed URL for an S3 object."""
    if not image_key:
        return None
    s3_key = f"{S3_FOLDER_NAME}{image_key}"
    try:
        return s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )
    except Exception as e:
        logger.error(f"Error generating pre-signed URL for key {s3_key}: {e}")
        return None


def fetch_product_categories():
    """Fetch distinct main categories and their subcategories."""
    conn = get_db_connection()
    if not conn:
        return {}
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT Main_Category, Sub_Categories FROM Products WHERE Main_Category IS NOT NULL AND Sub_Categories IS NOT NULL LIMIT 50;")
            rows = cur.fetchall()
            category_data = {}
            for main_cat, sub_cat in rows:
                if main_cat not in category_data:
                    category_data[main_cat] = []
                if sub_cat and sub_cat not in category_data[main_cat]:
                    category_data[main_cat].append(sub_cat)
            return category_data
    except Exception as e:
        logger.error(f"Error fetching product categories: {e}")
        return {}


# --- Context Processors and Teardown ---

@app.context_processor
def inject_categories():
    """Injects categories into all templates."""
    return dict(categories=fetch_product_categories())


@app.teardown_appcontext
def teardown_db(exception):
    """Ensures the database connection is closed after each request."""
    close_db_connection(exception)


# --- Core Routes ---

@app.route('/')
def home():
    logger.info("Home page requested")
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Database connection failed."), 500

    try:
        with conn.cursor() as cur:
            query = """
                SELECT Item_Code AS product_id, Product_Title AS product_name, Sub_Categories AS product_description, Price AS product_price, image_url
                FROM Products ORDER BY RANDOM() LIMIT 4;
            """
            cur.execute(query)
            random_products_raw = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            random_products = []
            for row in random_products_raw:
                product = dict(zip(column_names, row))
                product['product_image_url'] = generate_presigned_url(product['image_url'])
                random_products.append(product)

    except Exception as e:
        logger.error(f"An error occurred on the home page: {e}")
        return render_template('error.html', message="An error occurred while fetching products."), 500

    return render_template('index.html', random_products=random_products)


@app.route('/search/results')
def search_results_page():
    query = request.args.get('q', '').strip()
    logger.info(f"Search results page requested for query: '{query}'")
    if not query:
        return render_template('searchresult.html', products=[], query=query)

    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Database connection failed."), 500

    search_results = []
    try:
        with conn.cursor() as cur:
            sql_query = """
                SELECT Item_Code AS itemcode, Product_Title AS name, Sub_Categories AS subcategory, Product_Description AS description, Price AS price, image_url
                FROM Products WHERE Product_Title ILIKE %s OR Product_Description ILIKE %s;
            """
            cur.execute(sql_query, (f"%{query}%", f"%{query}%"))
            results = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            for row in results:
                product = dict(zip(column_names, row))
                product['image_url'] = generate_presigned_url(product['image_url'])
                search_results.append(product)
    except Exception as e:
        logger.error(f"Error executing search query: {e}")
        return render_template('error.html', error="An error occurred during search."), 500

    return render_template('searchresult.html', products=search_results, query=query)


# --- ✨ ADDED: Route for a single product's detail page ---
@app.route('/product/<string:itemcode>')
def product_details(itemcode):
    logger.info(f"Fetching details for product itemcode: {itemcode}")
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Database connection failed."), 500

    try:
        with conn.cursor() as cur:
            query = """
                SELECT Item_Code AS itemcode, Product_Title AS name, Sub_Categories AS subcategory, Product_Description AS description, Price AS price, image_url
                FROM Products WHERE Item_Code = %s;
            """
            cur.execute(query, (itemcode,))
            result = cur.fetchone()

            if not result:
                return render_template('product_not_found.html', itemcode=itemcode), 404

            column_names = [desc[0] for desc in cur.description]
            product = dict(zip(result, column_names))
            product['image_url'] = generate_presigned_url(product['image_url'])

            return render_template('product_details.html', product=product)

    except Exception as e:
        logger.error(f"Error fetching product details for {itemcode}: {e}")
        return render_template('error.html', message="Could not retrieve product details."), 500


@app.route('/<string:maincategory>')
def show_category_products(maincategory):
    logger.info(f"Fetching products for category: {maincategory}")
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Database connection failed."), 500

    product_list = []
    try:
        with conn.cursor() as cursor:
            query = "SELECT Item_Code AS itemcode, Product_Title AS productname, Sub_Categories AS subcategory, Price AS price, image_url FROM Products WHERE Main_Category = %s;"
            cursor.execute(query, (maincategory,))
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            for row in results:
                product = dict(zip(column_names, row))
                product['image_url'] = generate_presigned_url(product['image_url'])
                product_list.append(product)
    except Exception as e:
        logger.error(f"Error fetching products for category {maincategory}: {e}")
        return render_template('error.html', message="Error fetching products."), 500

    return render_template('category.html', maincategory=maincategory, products=product_list)


@app.route('/<string:maincategory>/<string:subcategory>')
def show_subcategory_products(maincategory, subcategory):
    logger.info(f"Fetching products for subcategory: {subcategory}")
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Database connection failed."), 500

    product_list = []
    try:
        with conn.cursor() as cursor:
            query = "SELECT Item_Code AS itemcode, Product_Title AS productname, Product_Description AS productdescription, Price AS price, image_url FROM Products WHERE Main_Category = %s AND Sub_Categories = %s;"
            cursor.execute(query, (maincategory, subcategory))
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            for row in results:
                product = dict(zip(column_names, row))
                product['image_url'] = generate_presigned_url(product['image_url'])
                product_list.append(product)
    except Exception as e:
        logger.error(f"Error fetching products for subcategory {subcategory}: {e}")
        return render_template('error.html', message="Error fetching products."), 500

    return render_template('subcategory.html', maincategory=maincategory, subcategory=subcategory,
                           products=product_list)


# --- ✨ ADDED: User Profile Routes ---

@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        flash('Unauthorized access. Please log in.', 'danger')
        return redirect(url_for('login1.login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET username = %s, email = %s, mobile_number = %s WHERE user_id = %s",
                               (username, email, mobile_number, user_id))
                conn.commit()
                flash('Profile updated successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error updating profile: {e}', 'danger')
        return redirect(url_for('edit_profile', user_id=user_id))

    # For GET request
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT username, email, mobile_number FROM users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            if not user_data:
                flash('User not found.', 'danger')
                return redirect(url_for('home'))
            user = {'username': user_data[0], 'email': user_data[1], 'mobile_number': user_data[2]}
            return render_template('edit_profile.html', user=user)
    except Exception as e:
        flash(f'Error fetching user data: {e}', 'danger')
        return redirect(url_for('home'))


@app.route('/edit_address/<int:user_id>', methods=['GET', 'POST'])
def edit_address(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        flash('Unauthorized access. Please log in.', 'danger')
        return redirect(url_for('login1.login'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        address = request.form['address']
        postal_code = request.form['postal_code']
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET address = %s, postal_code = %s WHERE user_id = %s",
                               (address, postal_code, user_id))
                conn.commit()
                flash('Address updated successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error updating address: {e}', 'danger')
        return redirect(url_for('edit_address', user_id=user_id))

    # For GET request
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT address, postal_code FROM users WHERE user_id = %s", (user_id,))
            address_data_raw = cursor.fetchone()
            address_data = {'address': '', 'postal_code': ''}
            if address_data_raw:
                address_data['address'] = address_data_raw[0]
                address_data['postal_code'] = address_data_raw[1]
            return render_template('edit_address.html', address_data=address_data)
    except Exception as e:
        flash(f'Error fetching address data: {e}', 'danger')
        return redirect(url_for('home'))


# --- Static and Info Routes ---
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


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


if __name__ == "__main__":
    logger.info("Starting Flask application in debug mode...")
    app.run(host='0.0.0.0', port=5000, debug=True)