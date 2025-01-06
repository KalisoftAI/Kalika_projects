from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import xml.etree.ElementTree as ET
from functools import wraps
from db import get_db_connection


cart1 = Blueprint('cart1', __name__)


# Route for cart page
@cart1.route('/cart', methods=['GET', 'POST'])
def cart():
    print("Debug: Entered the cart route")
    from app import get_shared_data
    shared_data = get_shared_data()
    categories = shared_data['categories']
    cart_items = session.get('cart', [])
    print("Debug: Cart Items",cart_items)

    if request.method == 'GET':
        for item in cart_items:
            item['total_price'] = item['quantity'] * item['price']
        total_amount = sum(item['total_price'] for item in cart_items)

        if request.headers.get('Accept') == 'application/json':
            return jsonify({"cart_items": cart_items, "total_amount": total_amount})
        else:
            return render_template('testcart.html', cart_items=cart_items, total_amount=total_amount, categories=categories)

    elif request.method == 'POST':
        data = request.get_json()
        itemcode = data.get('itemcode')
        action = data.get('action')

        if not itemcode or not action:
            return jsonify({"error": "Invalid request data"}), 400

        for item in cart_items:
            if item['itemcode'] == itemcode:
                if action == 'increase':
                    item['quantity'] += 1
                elif action == 'decrease':
                    item['quantity'] -= 1
                    if item['quantity'] <= 0:
                        cart_items.remove(item)
                elif action == 'remove':
                    cart_items.remove(item)
                break

        for item in cart_items:
            item['total_price'] = item['quantity'] * item['price']

        session['cart'] = cart_items
        session.modified = True
        total_amount = sum(item['total_price'] for item in cart_items)

        return jsonify({"cart_items": cart_items, "total_amount": total_amount})
    
@cart1.route('/cart/count', methods=['GET'])
def cart_count():
    cart_items = session.get('cart', [])
    total_items = sum(item['quantity'] for item in cart_items)
    return jsonify({"cart_count": total_items})


@cart1.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    print("in add to cart of cart.py")
    item_data = request.json
    cart_item = {
        'name': item_data['name'],
        'price': item_data['price'],
        'quantity': 1
    }
    # Store item in session (or database)
    if 'cart' not in session:
        session['cart'] = []
    # Check if item exists in the cart
    existing_item = next((item for item in session['cart'] if item['name'] == cart_item['name']), None)
    if existing_item:
        existing_item['quantity'] += 1
    else:
        session['cart'].append(cart_item)

    return jsonify({'success': True, 'cart': session['cart']})


# @cart1.route('/checkout', methods=['POST'])
# def checkout():
#     # print('session', session['cart'])
#     if 'cart' not in session or not session['cart']:
#         return jsonify({'success': False, 'message': 'Cart is empty'})
#     print('session',session)
#     # Generate punchout.xml file
#     punchout_xml = generate_punchout_xml(session['cart'], session.get('user_name'))
#     print('punchout xml',punchout_xml)
#
#     # Here you would typically save the XML to a file or send it somewhere
#     # with open('punchout.xml', 'w') as xml_file:
#     #     xml_file.write(punchout_xml)
#     # Connect to PostgreSQL
#     connection = get_db_connection()
#     if connection:
#         print("Database connection successful!")
#     else:
#         print("Failed to connect to the database.")
#     cursor = connection.cursor()
#
#     # Insert XML into the database
#     try:
#         query = "INSERT INTO punchout_responses (response) VALUES (%s)"
#         cursor.execute(query, (punchout_xml,))
#         connection.commit()
#         print("XML response saved successfully!")
#         cursor.close()
#         connection.close()
#     except Exception as e:
#         print("Error while inserting XML:", e)
#
#     print("checkout and punchout completed ")
#
#     # Clear the cart after checkout
#     session.pop('cart', None)
#
#     return jsonify({'success': True, 'message': 'Checkout successful', 'xml_file': 'punchout.xml'})



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print("User not logged in. Redirecting to login page.")
            return redirect(url_for('login1.login'))
        return f(*args, **kwargs)
    return decorated_function


@cart1.route('/checkout', methods=['POST'])
@login_required  # Enforce login check before executing the route
def checkout():
    print("In cart checkout.")
    if 'cart' not in session or not session['cart']:
        return jsonify({'success': False, 'message': 'Cart is empty'})
    
    if 'user_id' not in session:
        print("Error: Attempt to checkout without logging in.")
        return jsonify({'success': False, 'message': 'You must be logged in to checkout.'}), 403

    print("Starting XML generation...")
    punchout_xml = generate_punchout_xml(session['cart'], session.get('user_name'))
    print('Generated PunchOut XML:', punchout_xml)

    # Connect to PostgreSQL
    connection = get_db_connection()
    if not connection:
        print("Database connection failed.")
        return jsonify({'success': False, 'message': 'Database connection failed'})

    try:
        cursor = connection.cursor()
        query = "INSERT INTO punchout_responses (response) VALUES (%s)"
        cursor.execute(query, (punchout_xml,))
        connection.commit()
        print("PunchOut XML saved successfully.")
    except Exception as e:
        print("Error saving XML to database:", e)
        return jsonify({'success': False, 'message': 'Error saving XML.'})
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Clear the cart after checkout
    session.pop('cart', None)
    return jsonify({'success': True, 'message': 'Checkout successful'})



def generate_punchout_xml(cart_items, user_name):
    root = ET.Element("PunchOutOrder")

    buyer_element = ET.SubElement(root, "Buyer")
    ET.SubElement(buyer_element, "Name").text = user_name

    items_element = ET.SubElement(root, "Items")
    print("cart_items type::::", type(cart_items))
    print("cart_items::::", cart_items)

    for item in cart_items:

        item_element = ET.SubElement(items_element, "Item")
        ET.SubElement(item_element, "Name").text = item['name']
        ET.SubElement(item_element, "Quantity").text = str(item['quantity'])
        ET.SubElement(item_element, "Price").text = str(item['price'])

    return ET.tostring(root, encoding='unicode')