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
import boto3



# Initialize S3 client
s3 = boto3.client('s3', region_name='ap-south-1')
BUCKET_NAME = 'kalikaecom'
FOLDER_NAME = 'Folder/'  # Folder inside the S3 bucket



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

@app.context_processor
def inject_shared_data():
    """
    Automatically inject shared data (like categories) into all templates.
    """
    return get_shared_data()

def get_shared_data():
    """
    Fetch shared data such as categories.
    """
    return {
        "categories": fetch_productcatalog_data()  # Replace this with your actual function to fetch categories
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
               image_url AS product_image_key
        FROM product_catlog_image_url
        ORDER BY RANDOM()
        LIMIT 4;
    """

    # Fetch data using the connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(random_products_query)

    # Fetch column names
    column_names = [desc[0] for desc in cur.description]

    # Convert tuples to dictionaries and add pre-signed URLs for images
    random_products = []
    for row in cur.fetchall():
        product = dict(zip(column_names, row))

        # Generate pre-signed URL for the product image
        s3_key = f"{FOLDER_NAME}{product['product_image_key']}"  # Prefix folder to the key
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )
        product['product_image_url'] = presigned_url  # Add the image URL to the product dictionary
        random_products.append(product)
    # print("random_products:::", random_products)
    cur.close()
    conn.close()

    return render_template(
        'index.html',
        maincategory=maincategory,
        categories=categories,
        random_products=random_products
    )



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



@app.route('/search', methods=['GET'])
def search():
    term = request.args.get('q', '')  # Get the search term from query params
    if not term:
        return jsonify([])  # Return empty list if no search term is provided

    conn = get_db_connection()
    cur = conn.cursor()

    # Execute the SQL query to search for products matching the term
    cur.execute("""
        SELECT itemcode, productname, subcategory, price, image_url
        FROM product_catlog_image_url 
        WHERE productname ILIKE %s
    """, (f"%{term}%",))  # Case-insensitive match
    results = cur.fetchall()
     # Process results and add pre-signed URLs for images
    search_results = []
    for row in results:
        # Generate pre-signed URL for the product image
        s3_key = f"{FOLDER_NAME}{row[4]}"  # Prefix folder to the key
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )
        # print(presigned_url)
        search_results.append({
            "itemcode": row[0],
            "name": row[1],
            "subcategory": row[2],
            "price": row[3],
            "image_url": presigned_url
        })
    # print("results:", results)

    cur.close()
    return jsonify(search_results)


@app.route('/product/<itemcode>', methods=['GET'])
def get_product_details(itemcode):
    print("Fetching product details")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT itemcode, productname, subcategory, price, productdescription, image_url 
        FROM product_catlog_image_url 
        WHERE itemcode = %s
    """, (itemcode,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        # Generate pre-signed URL for the product image
        s3_key = f"{FOLDER_NAME}{result[5]}"  # Prefix folder to the key
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )
        # Render a detailed product page
        return render_template('product.html', product={
            "itemcode": result[0],
            "name": result[1],
            "subcategory": result[2],
            "price": result[3],
            "description": result[4],
            "image_url": presigned_url
        })
    else:
        # Render a "Product Not Found" page
        return render_template('product_not_found.html', itemcode=itemcode), 404
    


@app.route('/<string:maincategory>')
def show_category_products(maincategory):
    conn = get_db_connection()
    categories = fetch_productcatalog_data()
    cursor = conn.cursor()

    # Fetch products by category
    query = """
        SELECT itemcode, productname, subcategory, price, image_url
        FROM product_catlog_image_url 
        WHERE maincategory = %s;
    """
    cursor.execute(query, (maincategory,))
    productcatalog = cursor.fetchall()

    # Convert fetched data to a list of dictionaries
    product_list = []
    for row in productcatalog:
        s3_key = f"{FOLDER_NAME}{row[4]}"  # Prefix folder to the key
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )
        product_list.append({
            'itemcode': row[0],
            'productname': row[1],
            'subcategory': row[2],
            'price': row[3],
            'image_url': presigned_url
        })
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
        SELECT itemcode, productname, productdescription, price, image_url
         FROM product_catlog_image_url 
        WHERE maincategory = %s AND subcategory = %s;
    """
    cursor.execute(query, (maincategory, subcategory))
    productcatalog = cursor.fetchall()

    # Convert fetched data to a list of dictionaries
    product_list = []
    for row in productcatalog:
        s3_key = f"{'Folder/'}{row[4]}"
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )
        product_list.append({
            'itemcode': row[0],
            'productname': row[1],
            'productdescription': row[2],
            'price': row[3],
            'image_url': presigned_url
        })

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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.close()
    conn.close()


    
@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    print(f"Session contents: {session}")  # Debug
    print(f"Accessing edit_profile for user_id: {user_id}")  # Debug
    if 'user_id' not in session or session['user_id'] != user_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    if session['user_id'] != user_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile_number = request.form['mobile_number']

        try:
            cursor.execute("""
                UPDATE users
                SET username = %s, email = %s, mobile_number = %s
                WHERE user_id = %s
            """, (username, email, mobile_number, user_id))
            conn.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error updating profile: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('edit_profile', user_id=user_id))

    try:
        cursor.execute("SELECT username, email, mobile_number FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error fetching user data: {e}', 'danger')
        return redirect(url_for('home'))
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('edit_profile', user_id=session.get('user_id')))



@app.route('/edit_address/<int:user_id>', methods=['GET', 'POST'])
def edit_address():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in to access this page.', 'danger')
        return redirect(url_for('login'))  # Replace 'login' with your actual login route

    user_id = session['user_id']  # Fetch user_id from the session

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get form data
        address = request.form['address']
        postal_code = request.form['postal_code']

        # Update address in the database
        try:
            cursor.execute("""
                UPDATE users
                SET address = %s, postal_code = %s
                WHERE user_id = %s
            """, (address, postal_code, user_id))
            conn.commit()
            flash('Address updated successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error updating address: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

        # Redirect to the same edit page
        return redirect(url_for('edit_address'))
    
    # Fetch address information to pre-fill the form
    try:
        cursor.execute("SELECT address, postal_code FROM users WHERE user_id = %s", (user_id,))
        address_data = cursor.fetchone()
        if not address_data:
            flash('Address not found.', 'danger')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error fetching address data: {e}', 'danger')
        return redirect(url_for('home'))
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_address.html', address_data=address_data)


def fetch_productcatalog_data():
    """Fetch maincategory and subcategory data from the database."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT maincategory, subcategory
            FROM product_catlog_image_url LIMIT 15;
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
        # print("maincategories", maincategories)
        cursor.close()
        connection.close()

        # Add a default image for each category
        return [{'name': row[0], 'image': 'path/to/default/image.jpg'} for row in maincategories]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

if __name__ == "__main__":
    app.run(debug=True)

