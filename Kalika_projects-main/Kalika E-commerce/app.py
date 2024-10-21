from flask import Flask, request, jsonify, render_template, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
from punchout import *
from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
import xml.etree.ElementTree as ET

app = Flask(__name__)

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Sample user data (in a real app, use a database)
users = {
    "admin": bcrypt.generate_password_hash("password123").decode('utf-8'),  # Hashed password
}


@app.route('/punchout', methods=['POST'])
def punchout():
    cart_items = request.json.get('cartItems', [])

    # Create XML structure
    punchout_order = ET.Element("PunchOutOrder")

    for item in cart_items:
        product_element = ET.SubElement(punchout_order, "Product")
        ET.SubElement(product_element, "ProductID").text = str(item['product_id'])
        ET.SubElement(product_element, "ProductName").text = item['name']
        ET.SubElement(product_element, "Quantity").text = str(item['quantity'])
        ET.SubElement(product_element, "Price").text = str(item['price'])

    xml_str = ET.tostring(punchout_order, encoding='utf-8', method='xml').decode('utf-8')

    # Return XML response
    return xml_str, 200, {'Content-Type': 'application/xml'}


# Other routes remain unchanged...



# @app.route('/login_page')
# def home():
#     return render_template('login.html')  # Render the login form
#
#
# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form.get('username')
#     password = request.form.get('password')
#
#     # Check if the username exists
#     if username in users:
#         # Verify the password against the stored hash
#         if bcrypt.check_password_hash(users[username], password):
#             flash("Welcome to the Kalika E-Commerce.")
#             return redirect(url_for('dashboard'))
#
#     # If authentication fails
#     flash("Invalid username or password. Please try again.")
#     return redirect(url_for('home'))  # Redirect back to the login page
#

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='postgres',
        user='postgres',
        password='Kalika@1992'
    )
    return conn

get_db_connection()
@app.route('/checkout', methods=['POST'])
def checkout():
    cart_items = request.json.get('cartItems', [])
    user_id = request.json.get('userId')  # Assuming you have user ID from session or input

    # Create a new order
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('INSERT INTO Orders (user_id, status) VALUES (%s, %s) RETURNING order_id',
                (user_id, 'Pending'))
    order_id = cur.fetchone()[0]  # Get the newly created order ID

    # Insert order items
    for item in cart_items:
        cur.execute('INSERT INTO OrderItems (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)',
                    (order_id, item['product_id'], item['quantity'], item['price']))

    print("Data inserted after checkout ")
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Order placed successfully!', 'order_id': order_id}), 200

# Route for displaying products
@app.route('/products')
def products():
    conn = get_db_connection()
    cur = conn.cursor()
    assert isinstance(cur, object)
    cur.execute(
        'SELECT Product_Title as name, Product_Description as description, Price as price, image_url FROM kalika_catalog LIMIT 10;')
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/punchout', methods=['GET'])
# def punchout():
#     xml_response = create_punchout_request()
#
#     return Response(xml_response, mimetype='application/xml')


# Route for about us page
@app.route('/about')
def about():
    return render_template('aboutus.html')

    # Route for cart page
#
#
@app.route('/cart.html')
def cart():
    return render_template('cart.html')




# Route for contact us page
@app.route('/contact.html')
def contact():
    return render_template('contactus.html')


# Route for dashboard
@app.route('/dashboard.html')
def dashboard():
    return render_template('dash.html')


# Route for payment page
@app.route('/payment.html')
def payment():
    return render_template('payment.html')


# Route for register page
@app.route('/register.html')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
