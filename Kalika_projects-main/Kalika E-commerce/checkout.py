from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
from datetime import datetime
from addtocart import add_cart
import xml.etree.ElementTree as ET
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from datetime import datetime
# from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, request, Response

check = Blueprint('check', __name__)

@check.route('/punchout/setup', methods=['GET', 'POST'])
def punchout_setup():
    # Handle PunchOut Setup Request (POSR)
    if request.method == 'POST':
        # Extract necessary data from request
        user_data = request.form  # Assuming data is sent in form

        # Generate PunchOut Setup Response (POSR)
        response = generate_punchout_response(user_data)
        return response  # Return XML response


def generate_punchout_response(user_data):
    # Create the root element for the response
    cxml = ET.Element('cXML', version="1.2.020", payloadID="1234567890", timestamp=datetime.utcnow().isoformat() + 'Z')

    # Create Header
    header = ET.SubElement(cxml, 'Header')

    # From
    from_elem = ET.SubElement(header, 'From')
    credential_from = ET.SubElement(from_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_from, 'Identity').text = user_data.get('from_identity', "123456789")

    # To
    to_elem = ET.SubElement(header, 'To')
    credential_to = ET.SubElement(to_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_to, 'Identity').text = user_data.get('to_identity', "987654321")

    # Sender
    sender_elem = ET.SubElement(header, 'Sender')
    credential_sender = ET.SubElement(sender_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_sender, 'Identity').text = user_data.get('sender_identity', "555555555")
    ET.SubElement(credential_sender, 'SharedSecret').text = user_data.get('shared_secret', "secret123")
    ET.SubElement(sender_elem, 'UserAgent').text = user_data.get('user_agent', "YourAppName/1.0")

    # Create Response
    response_elem = ET.SubElement(cxml, 'Response')

    # PunchOutSetupResponse
    punchout_response = ET.SubElement(response_elem, 'PunchOutSetupResponse', status="200",
                                      id=user_data.get('request_id', "PO12345"))

    # Add relevant information based on user data
    ET.SubElement(punchout_response, 'BuyerCookie').text = user_data.get('buyer_cookie', "cookieValue")

    # Redirect URL
    redirect_url = ET.SubElement(punchout_response  , 'RedirectURL')
    redirect_url.text = user_data.get('redirect_url', "https://example.com/redirect")

    # Supplier Setup Confirmation
    supplier_setup = ET.SubElement(punchout_response, 'SupplierSetup')
    ET.SubElement(supplier_setup, 'SupplierID').text = user_data.get('supplier_id', "SupplierID123")

    # Generate XML string
    xml_str = ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')

    return xml_str

def create_punchout_request():
    # Create the root element
    cxml = ET.Element('cXML', version="1.2.020", payloadID="1234567890", timestamp=datetime.utcnow().isoformat() + 'Z')

    # Create Header
    header = ET.SubElement(cxml, 'Header')

    # From
    from_elem = ET.SubElement(header, 'From')
    credential_from = ET.SubElement(from_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_from, 'Identity').text = "123456789"

    # To
    to_elem = ET.SubElement(header, 'To')
    credential_to = ET.SubElement(to_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_to, 'Identity').text = "987654321"

    # Sender
    sender_elem = ET.SubElement(header, 'Sender')
    credential_sender = ET.SubElement(sender_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_sender, 'Identity').text = "555555555"
    ET.SubElement(credential_sender, 'SharedSecret').text = "secret123"
    ET.SubElement(sender_elem, 'UserAgent').text = "YourAppName/1.0"

    # Create Request
    request_elem = ET.SubElement(cxml, 'Request', deploymentMode="test")

    # PunchOutSetupRequest
    punchout_request = ET.SubElement(request_elem, 'PunchOutSetupRequest', operation="create", id="PO12345")
    ET.SubElement(punchout_request, 'BuyerCookie').text = "cookieValue"

    redirect_url = ET.SubElement(punchout_request, 'RedirectURL')
    redirect_url.text = "https://darkviolet-seal-221814.hostingersite.com/punchout.xml?vid=123456&sessionid=session123"

    supplier_setup = ET.SubElement(punchout_request, 'SupplierSetup')
    ET.SubElement(supplier_setup, 'SupplierID').text = "SupplierID123"

    # Generate XML string
    xml_str = ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')
    print(xml_str)
    return xml_str




# @app.route('/punchout_setup', methods=['POST'])
# def punch_out_setup():
#     # Get the cXML input (from the buyer's procurement system)
#     input_data = request.data.decode('utf-8')
#
#     # Load cXML request into ElementTree for parsing
#     cxml = ET.fromstring(input_data)
#
#     # Parse important data from the PunchOutSetupRequest
#     buyer_cookie = cxml.find('.//BuyerCookie').text
#     operation = cxml.find('.//Operation').text
#
#
#     # Define PunchOut URL where the buyer will be redirected to complete shopping
#     punchout_url = f"https://lemonchiffon-ram-961910.hostingersite.com?session={buyer_cookie}"
#
#     # Create the PunchOutSetupResponse XML
#     response_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
#     <cXML payloadID="{uuid.uuid4()}" timestamp="{datetime.datetime.now().isoformat()}" version="1.2.010">
#         <Response>
#             <PunchOutSetupResponse>
#                 <StartPage>
#                     <URL>{punchout_url}</URL>
#                 </StartPage>
#             </PunchOutSetupResponse>
#         </Response>
#     </cXML>'''
#
#     return Response(response_xml, content_type='application/xml')
#
create_punchout_request()
@check.route('/checkout', methods=['POST'])
def checkout():
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Retrieve form data
    user_name = request.form.get('user_name')
    shipping_address = request.form.get('shipping_address')
    total_amount = float(request.form.get('total_amount', 0))
    payment_status = request.form.get('payment_status')
    order_date = datetime.now()
    cart_items = session.get('cart', [])

    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for('home'))

    try:
        # Find user_id from Users table using user_name
        cursor.execute("SELECT user_id FROM Users WHERE username = %s", (user_name,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            # Insert the order into the Orders table
            cursor.execute('''
                INSERT INTO Orders (user_id, order_date, total_amount, status, shipping_address, payment_status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING order_id
            ''', (user_id, order_date, total_amount, 'pending', shipping_address, payment_status, order_date, order_date))
            order_id = cursor.fetchone()[0]

            # Insert each cart item into the OrderItems table
            for item in cart_items:
                product_id = item['product_id']
                quantity = item['quantity']
                price = item['price']  # Assuming each item has a price field

                cursor.execute('''
                    INSERT INTO OrderItems (order_id, product_id, quantity, price, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (order_id, product_id, quantity, price, order_date, order_date))

            # Commit transaction
            connection.commit()

            # Flash success message and clear cart
            flash("Order placed successfully!", "success")
            session.pop('cart', None)  # Clears the entire cart

            return redirect(url_for('home'))
        else:
            flash("User not found. Please check your name.", "error")
            return redirect(url_for('cart1.cart'))  # Redirects to cart for retry

    except Exception as e:
        connection.rollback()
        flash(f"Error placing order: {e}", "error")
        return redirect(url_for('cart1.cart'))  # Redirects to cart for retry in case of error

    finally:
        cursor.close()
        connection.close()
