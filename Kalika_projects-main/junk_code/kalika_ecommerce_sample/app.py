# app.py
from flask import Flask, render_template, request, jsonify,session
# from sap_integration import SAPIntegration
from database import Database
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
db = Database()

# cart_items = request.json['cart_items']
# order = db.create_order(cart_items)

# print(f'oder{order}')
# sap = SAPIntegration()

# Database connection
# def get_db_connection():
#     conn = psycopg2.connect(
#         host="localhost",
#         database="postgres",
#         user="postgres",
#         password="Kalika@1992"
#     )
#     return conn
# conn = get_db_connection()
# cur = conn.cursor(cursor_factory=RealDictCursor)
# cur.execute('SELECT * FROM products')
# products_data = cur.fetchall()

products=['Handgloves','Tarpaulin','strechfilm','Others'] ## testing

@app.route('/')
def index():
    # products = db.get_products()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = db.get_product(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.json['product_id']
    quantity = request.json['quantity']

    # Initialize the cart in the session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}

    # Update the quantity of the product in the cart
    if product_id in session['cart']:
        session['cart'][product_id] += quantity
    else:
        session['cart'][product_id] = quantity

    # Save the updated cart back to the session
    session.modified = True

    return jsonify({'success': True, 'cart': session['cart']})


@app.route('/checkout', methods=['POST'])
def checkout():
    cart_items = request.json['cart_items']
    # Process the order
    order = db.create_order(cart_items)
    print(f'oder{order}')
    # Send order to SAP
    # order_id=1
    # sap_order_id = sap.create_order(order)
    sap_order_id = 1
    return jsonify({'order_id': order.id, 'sap_order_id': sap_order_id})
#     return jsonify({'order_id': order_id, 'sap_order_id': sap_order_id})

if __name__ == '__main__':
    app.run(debug=True)

