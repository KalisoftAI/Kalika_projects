import os
from flask import Flask, request, jsonify, render_template, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
import xml.etree.ElementTree as ET
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="Kalika@1992"
    )
    return conn


# Create tables
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    # Drop the existing products table if it exists
    cur.execute("DROP TABLE IF EXISTS products;")
    cur.execute('''CREATE TABLE IF NOT EXISTS products
                   (id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    image_url TEXT NOT NULL);''')
    cur.execute('''CREATE TABLE IF NOT EXISTS punchout_sessions
                   (id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL UNIQUE,
                    buyer_cookie VARCHAR(100),
                    return_url TEXT NOT NULL);''')
    conn.commit()
    cur.close()
    conn.close()





# Add sample products
def add_sample_products():
    conn = get_db_connection()
    cur = conn.cursor()

    # Clear existing products
    cur.execute("DELETE FROM products;")

    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        sample_products = [
            (1,"LED lights", 999.99, "/static/images/Handgloves.jpg"),
            (2,"stretchfilm", 699.99, "/static/images/Stretchfilm.jpg"),
            (3,"Handgloves", 199.99, "/static/images/s3.jpg"),
            (4,"tarpaulin", 499.99, "/static/images/s4.jpg"),
        ]
        cur.executemany("INSERT INTO products (id,name, price, image_url) VALUES (%s,%s, %s, %s)", sample_products)
        conn.commit()
    cur.close()
    conn.close()

create_tables()
add_sample_products()

products=['Handgloves','Tarpaulin','strechfilm','Others']
# Routes
@app.route('/')
def index():
    return render_template('index.html',products=products)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM products')
    products = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(products)


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


if __name__ == '__main__':
    app.run(debug=True)
