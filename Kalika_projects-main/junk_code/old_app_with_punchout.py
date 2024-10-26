from flask import Flask, render_template
import psycopg2
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
import xml.etree.ElementTree as ET
from werkzeug.middleware.proxy_fix import ProxyFix
# app = Flask(__name__)

# from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import os
from datetime import datetime


from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection function
def connect_db():
    return psycopg2.connect(
        host='localhost',
        database='postgres',
        user='postgres',
        password='Vikas@1992'

    )



# Route for homepage
@app.route('/')
def index():
    return render_template('index_test.html')

@app.route('/products')
def products():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT Product_Title as name, Product_Description as description, Price as price, image_url FROM kalika_catalog LIMIT 10;')
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query', '')
    
    if query:
        conn = connect_db()
        cur = conn.cursor()
        search_query = f"%{query}%"
        
        # Use ILIKE for case-insensitive search
        cur.execute("SELECT Product_Title as name, image_url, Price as price FROM kalika_catalog WHERE Product_Title ILIKE %s", (search_query,))
        products = cur.fetchall()
        cur.close()
        conn.close()
        
        results = [{'id': idx, 'name': product[0], 'image_url': product[1], 'price': product[2]} for idx, product in enumerate(products)]
        return jsonify(results)
    
    return jsonify([])

## for category and subcategory
import pandas as pd
catalog_df = pd.read_csv('../data/kalika_catalog_products.csv')

@app.route('/')
def home():
    return render_template('index_test.html')

@app.route('/products/<category>')
def show_category(category):
    products = catalog_df[catalog_df['Main Category'] == category].to_dict(orient='records')
    return render_template('category.html', products=products, category=category)

@app.route('/products/<category>/<subcategory>')
def show_subcategory(category, subcategory):
    products = catalog_df[(catalog_df['Main Category'] == category) & (catalog_df['Sub Categories'] == subcategory)].to_dict(orient='records')
    return render_template('subcategory.html', products=products, category=category, subcategory=subcategory)
### test code end

# # Route for displaying products
# @app.route('/')
# def products():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute('SELECT Product_Title as name, Product_Description as description, Price as price, image_url FROM kalika_catalog LIMIT 10;')
#     products = cur.fetchall()
#     cur.close()
#     conn.close()
#     return render_template('products.html', products=products)

# Route for about us page
@app.route('/about')
def about():
    return render_template('aboutus.html')

# Route for cart page
@app.route('/cart')
def cart():
    return render_template('cart.html')

# Route for checkout page
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

# Route for contact us page
@app.route('/contact')
def contact():
    return render_template('contactus.html')

# Route for dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dash.html')

# Route for login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route for payment page
@app.route('/payment')
def payment():
    return render_template('payment.html')

# Route for register page
@app.route('/register')
def register():
    return render_template('register.html')

# Route for search functionality
# @app.route('/search')
# def search():
#     return render_template('search.html')

# Route for search suggestions (returns only product names)
@app.route('/suggest')
def suggest():
    query = request.args.get('query')
    
    if query:
        conn = connect_db()
        cur = conn.cursor()

        # Query to fetch product names matching the query
        suggest_query = "SELECT id, name FROM products WHERE name ILIKE %s LIMIT 10"
        cur.execute(suggest_query, (f"%{query}%",))
        products = cur.fetchall()

        cur.close()
        conn.close()

        # Create a list of dictionaries with product id and name
        product_list = [{'id': p[0], 'name': p[1]} for p in products]

        return jsonify(product_list)
    
    return jsonify([])  # Return an empty list if no query

# Route for product detail page
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = connect_db()
    cur = conn.cursor()

    detail_query = "SELECT name, price, image_url FROM products WHERE id = %s"
    cur.execute(detail_query, (product_id,))
    product = cur.fetchone()

    cur.close()
    conn.close()

    if product:
        return render_template('product_detail.html', product={
            'name': product[0],
            'price': product[1],
            'image_url': product[2]
        })
    else:
        return "Product not found", 404

# Test cart page route
@app.route('/test_cart')
def test_cart():
    return render_template('test_cart.html')

@app.route('/api/punchout/setup', methods=['POST'])
def punchout_setup():
    # Parse the incoming cXML request
    cxml = ET.fromstring(request.data)
    buyer_cookie = cxml.find(".//BuyerCookie").text
    return_url = cxml.find(".//URL").text

    # Generate a unique session ID
    session_id = os.urandom(16).hex()

    # Store the session information
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO punchout_sessions (session_id, buyer_cookie, return_url) VALUES (%s, %s, %s)",
                (session_id, buyer_cookie, return_url))
    conn.commit()
    cur.close()
    conn.close()

    # Prepare the cXML response
    response = ET.Element("cXML")
    response.set("payloadID", "response-" + os.urandom(16).hex())
    response.set("timestamp", "2024-10-02T12:00:00")

    resp = ET.SubElement(response, "Response")
    status = ET.SubElement(resp, "Status")
    status.set("code", "200")
    status.set("text", "OK")

    punchout = ET.SubElement(resp, "PunchOutSetupResponse")
    start_page = ET.SubElement(punchout, "StartPage")
    url = ET.SubElement(start_page, "URL")
    url.text = f"http://yourdomain.com/?session={session_id}"

    return ET.tostring(response), 200, {'Content-Type': 'text/xml'}


@app.route('/api/punchout/checkout', methods=['POST'])
def punchout_checkout():
    cart_items = request.json['items']

    # In a real application, you would process the cart items here
    # For this example, we'll just return a dummy cXML PunchOutOrderMessage

    # Retrieve the return URL from the session
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT return_url FROM punchout_sessions ORDER BY id DESC LIMIT 1")
    return_url = cur.fetchone()[0]
    cur.close()
    conn.close()

    # Prepare the cXML PunchOutOrderMessage
    order_message = ET.Element("cXML")
    order_message.set("payloadID", "order-" + os.urandom(16).hex())
    order_message.set("timestamp", "2024-10-02T12:00:00")

    header = ET.SubElement(order_message, "Header")
    # Add necessary header information here

    message = ET.SubElement(order_message, "Message")
    punchout_order_message = ET.SubElement(message, "PunchOutOrderMessage")
    # Add order details here based on cart_items

    # In a real application, you would send this message to the Ariba network
    # For this example, we'll just return the return URL

    return jsonify({"returnUrl": return_url})


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
