from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import xml.etree.ElementTree as ET
from db import get_db_connection


cart1 = Blueprint('cart1', __name__)


# Route for cart page
@cart1.route('/cart', methods=['GET', 'POST'])
def cart():
        if request.method == 'GET':
            # Handle GET request to fetch cart data
            cart_items = session.get('cart', [])
            print("cart_items",cart_items)
            if request.headers.get('Accept') == 'application/json':  # Check if the request expects JSON
                return jsonify({"cart_items": cart_items})  # Return JSON response
            else:
                return render_template('testcart.html', cart_items=cart_items)

        elif request.method == 'POST':
            # Handle POST request to update the cart
            cart_items = session.get('cart', [])
            data = request.get_json()
            print("data:::", data)
            item_id = data.get('id')
            action = data.get('action')

            # Find the item in the cart
            for item in cart_items:
                if item['id'] == item_id:
                    if action == 'increase':
                        item['quantity'] += 1
                    elif action == 'decrease':
                        item['quantity'] -= 1
                        if item['quantity'] <= 0:  # Remove item if quantity is 0
                            cart_items.remove(item)
                    elif action == 'remove':
                        cart_items.remove(item)
                    break

            # Update the session data
            session['cart'] = cart_items

            # Return updated cart items in the response

        return render_template('testcart.html', user_name=session.get('user_name'))


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

@cart1.route('/checkout', methods=['POST'])
def checkout():
    print("in cart checkout ")
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
    print("cart_items type::::", type(cart_items))
    print("cart_items::::", cart_items)

    for item in cart_items:

        item_element = ET.SubElement(items_element, "Item")
        ET.SubElement(item_element, "Name").text = item['name']
        ET.SubElement(item_element, "Quantity").text = str(item['quantity'])
        ET.SubElement(item_element, "Price").text = str(item['price'])

    return ET.tostring(root, encoding='unicode')