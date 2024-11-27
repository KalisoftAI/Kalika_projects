from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import xml.etree.ElementTree as ET
from db import get_db_connection
from datetime import datetime
from addtocart import add_cart

check = Blueprint('check', __name__)


@check.route('/checkout', methods=['POST'])
def checkout():
    print("in checkout")
    if 'cart' not in session or not session['cart']:
        return jsonify({'success': False, 'message': 'Cart is empty'})

    print("Starting XML generation...")
    punchout_xml = generate_punchout_xml(session['cart'], session.get('user_name'))
    print('punchout xml type', type(punchout_xml))
    print('punchout xml', punchout_xml)


    # Connect to PostgreSQL
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to the database.")
        return jsonify({'success': False, 'message': 'Database connection failed'})
    print("Database connection successful!")

    try:
        cursor = connection.cursor()
        query = "INSERT INTO punchout_responses (response) VALUES (%s)"
        cursor.execute(query, (punchout_xml,))
        connection.commit()
        print("XML response saved successfully!")
    except Exception as e:
        print("Error while inserting XML:", e)
        return jsonify({'success': False, 'message': 'Error saving XML'})
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    print("Checkout and PunchOut completed.")

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