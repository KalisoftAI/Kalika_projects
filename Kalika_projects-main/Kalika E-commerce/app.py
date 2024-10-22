from punchout import *
from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2

app = Flask(__name__)


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



# Route for cart page
@app.route('/cart.html')
def cart():
    return render_template('cart.html')


if __name__ == '__main__':
    app.run(debug=True)
