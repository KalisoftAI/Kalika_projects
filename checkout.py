from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import xml.etree.ElementTree as ET
from db import get_db_connection
from datetime import datetime
from add_cart import add_cart
from functools import wraps

check = Blueprint('check', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print("User not logged in. Redirecting to login page.")
            return redirect(url_for('login1.login'))
        return f(*args, **kwargs)
    return decorated_function

@check.route('/checkout', methods=['POST'])
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

    for item in cart_items:

        item_element = ET.SubElement(items_element, "Item")
        ET.SubElement(item_element, "Name").text = item['name']
        ET.SubElement(item_element, "Quantity").text = str(item['quantity'])
        ET.SubElement(item_element, "Price").text = str(item['price'])

    return ET.tostring(root, encoding='unicode')