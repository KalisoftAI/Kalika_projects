
from flask import Flask, render_template
import psycopg2
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
import xml.etree.ElementTree as ET
from werkzeug.middleware.proxy_fix import ProxyFix
app = Flask(__name__)

from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import os
from datetime import datetime

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='postgres',
        user='postgres',
        password='komal17'
    )
    return conn

# Route for displaying products
@app.route('/')
def products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT Product_Title as name, Product_Description as description, Price as price, image_url FROM kalika_catalog LIMIT 10;')
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('products.html', products=products)

# @app.route('/punchout', methods=['POST'])
# def punchout_setup():
#     # Parse the incoming cXML request
#     cxml = ET.fromstring(request.data)
#     buyer_cookie = cxml.find(".//BuyerCookie").text
#     return_url = cxml.find(".//URL").text
#
#     # Generate a unique session ID
#     session_id = os.urandom(16).hex()
#
#     # Store the session information
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO punchout_sessions (session_id, buyer_cookie, return_url) VALUES (%s, %s, %s)",
#                 (session_id, buyer_cookie, return_url))
#     conn.commit()
#     cur.close()
#     conn.close()
#
#     # Prepare the cXML response
#     response = ET.Element("cXML")
#     response.set("payloadID", "response-" + os.urandom(16).hex())
#     response.set("timestamp", "2024-10-02T12:00:00")
#
#     resp = ET.SubElement(response, "Response")
#     status = ET.SubElement(resp, "Status")
#     status.set("code", "200")
#     status.set("text", "OK")
#
#     punchout = ET.SubElement(resp, "PunchOutSetupResponse")
#     start_page = ET.SubElement(punchout, "StartPage")
#     url = ET.SubElement(start_page, "URL")
#     url.text = f"http://yourdomain.com/?session={session_id}"
#
#     return ET.tostring(response), 200, {'Content-Type': 'text/xml'}


request.data ="""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE cXML SYSTEM "http://xml.cXML.org/schemas/cXML/1.2.040/cXML.dtd">
<cXML payloadID="1234567890@example.com" timestamp="2024-10-08T12:00:00">
    <Header>
        <From>
            <Credential domain="DUNS">
                <Identity>buyerDUNS</Identity>
            </Credential>
        </From>
        <To>
            <Credential domain="DUNS">
                <Identity>supplierDUNS</Identity>
            </Credential>
        </To>
        <Sender>
            <Credential domain="NetworkId">
                <Identity>buyerNetworkId</Identity>
            </Credential>
            <UserAgent>My eProcurement System</UserAgent>
        </Sender>
    </Header>
    <Request deploymentMode="production">
        <PunchOutSetupRequest operation="create">
            <BrowserFormPost>
                <URL>https://ecommerce2.avetti.ca/preview/kalikaindiastore/</URL>
            </BrowserFormPost>
            <ShipTo>
                <Address addressID="TEST">
                    <Name xml:lang="en">John Doe</Name>
                    <PostalAddress>
                        <Street>123 Main St</Street>
                        <City>Anytown</City>
                        <State>CA</State>
                        <PostalCode>90210</PostalCode>
                        <Country isoCountryCode="US">US</Country>
                    </PostalAddress>
                </Address>
            </ShipTo>
        </PunchOutSetupRequest>
    </Request>
</cXML>
"""
@app.route('/punchout', methods=['POST'])
def punchout_setup():
    # Parse incoming cXML request
    cxml = ET.fromstring(request.data)

    # Extract BuyerCookie and URL
    buyer_cookie = cxml.find(".//BuyerCookie")
    return_url = "https://ecommerce2.avetti.ca/preview/kalikaindiastore/"  # Example return URL

    # Validate credentials (not shown here)

    # Generate a unique session ID
    session_id = os.urandom(16).hex()

    # Store session info in a database or temporary storage

    # Prepare cXML response
    response = ET.Element("cXML")
    response.set("payloadID", "response-" + os.urandom(16).hex())
    response.set("timestamp", datetime.now().isoformat())

    resp = ET.SubElement(response, "Response")
    status = ET.SubElement(resp, "Status")
    status.set("code", "200")
    status.set("text", "OK")

    punchout_response = ET.SubElement(resp, "PunchOutSetupResponse")
    start_page = ET.SubElement(punchout_response, "StartPage")
    url = ET.SubElement(start_page, "URL")
    url.text = f"https://ecommerce2.avetti.ca/preview/kalikaindiastore/punchout?session={session_id}"

    return Response(ET.tostring(response), content_type='text/xml')

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
