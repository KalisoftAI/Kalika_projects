import xml.etree.ElementTree as ET
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from datetime import datetime
# from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, request, Response

@check.route('/punchout/setup', methods=['GET', 'POST'])
def punchout_setup():
    # Handle PunchOut Setup Request (POSR)
    if request.method == 'POST':
        # Extract necessary data from request
        user_data = request.form  # Assuming data is sent in form
        print(user_data)
        # Generate PunchOut Setup Response (POSR)
        response = generate_punchout_response(user_data)
        return response  # Return XML response

def generate_punchout_response(user_data):
    """
    Generate a PunchOut Setup Response (POSR) in XML format.

    Parameters:
        user_data (dict): The data received from the PunchOut Setup Request (e.g., buyer details).

    Returns:
        str: An XML string representing the PunchOut Setup Response.
    """
    # Create the root element
    cxml = ET.Element('cXML', version="1.2.020", payloadID="response_1234567890",
                      timestamp=datetime.utcnow().isoformat() + 'Z')

    # Create Header
    header = ET.SubElement(cxml, 'Header')

    # From
    from_elem = ET.SubElement(header, 'From')
    credential_from = ET.SubElement(from_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_from, 'Identity').text = user_data.get('buyer_identity', 'UnknownBuyer')

    # To
    to_elem = ET.SubElement(header, 'To')
    credential_to = ET.SubElement(to_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_to, 'Identity').text = user_data.get('supplier_identity', 'UnknownSupplier')

    # Sender
    sender_elem = ET.SubElement(header, 'Sender')
    credential_sender = ET.SubElement(sender_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_sender, 'Identity').text = "555555555"
    ET.SubElement(credential_sender, 'SharedSecret').text = "response_secret"
    ET.SubElement(sender_elem, 'UserAgent').text = "YourAppName/1.0"

    # PunchOutSetupResponse
    response_elem = ET.SubElement(cxml, 'Response')
    status_elem = ET.SubElement(response_elem, 'Status', code="200", text="OK")
    status_elem.text = "PunchOut Setup Response Generated Successfully"

    # PunchOutSetupResponse Details
    punchout_response = ET.SubElement(response_elem, 'PunchOutSetupResponse')
    start_page = ET.SubElement(punchout_response, 'StartPage')
    start_page_url = ET.SubElement(start_page, 'URL')
    start_page_url.text = "https://darkviolet-seal-221814.hostingersite.com/punchout/start"

    # Generate XML string
    xml_str = ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')
    print(xml_str)  # Optional: Print for debugging
    return xml_str


#how to get duns number and other credentials
# duns number supplier = 651009354
# anid = AN01052123957
# Sum/gsm 167428


# from flask import request, Response
# import xml.etree.ElementTree as ET
# from datetime import datetime
#
# @check.route('/punchout/setup', methods=['POST'])
# def punchout_setup():
#     # Parse incoming XML
#     posr_xml = request.data.decode('utf-8')
#     root = ET.fromstring(posr_xml)
#
#     # Extract BuyerCookie (mandatory field in Ariba POSR)
#     buyer_cookie = root.find(".//BuyerCookie").text
#     buyer_identity = root.find(".//From/Credential/Identity").text
#     supplier_identity = root.find(".//To/Credential/Identity").text
#
#     # Generate the PunchOut Setup Response
#     response = generate_punchout_response({
#         'buyer_cookie': buyer_cookie,
#         'buyer_identity': buyer_identity,
#         'supplier_identity': supplier_identity
#     })
#
#     # Return the response to Ariba
#     return Response(response, content_type='text/xml')


# def generate_punchout_response(user_data):
#     cxml = ET.Element('cXML', version="1.2.020", payloadID="response_1234567890", timestamp=datetime.utcnow().isoformat() + 'Z')
#
#     # Header
#     header = ET.SubElement(cxml, 'Header')
#     from_elem = ET.SubElement(header, 'From')
#     ET.SubElement(from_elem, 'Credential', domain="DUNS").text = user_data['buyer_identity']
#
#     to_elem = ET.SubElement(header, 'To')
#     ET.SubElement(to_elem, 'Credential', domain="DUNS").text = user_data['supplier_identity']
#
#     sender_elem = ET.SubElement(header, 'Sender')
#     ET.SubElement(sender_elem, 'Credential', domain="DUNS").text = "555555555"
#     ET.SubElement(sender_elem, 'SharedSecret').text = "response_secret"
#     ET.SubElement(sender_elem, 'UserAgent').text = "YourAppName/1.0"
#
#     # Response with RedirectURL
#     response_elem = ET.SubElement(cxml, 'Response')
#     status_elem = ET.SubElement(response_elem, 'Status', code="200", text="OK")
#     punchout_response = ET.SubElement(response_elem, 'PunchOutSetupResponse')
#
#     start_page = ET.SubElement(punchout_response, 'StartPage')
#     redirect_url = ET.SubElement(start_page, 'URL')
#     redirect_url.text = f"https://yourdomain.com/punchout/session?buyerCookie={user_data['buyer_cookie']}"
#
#     # Generate XML
#     return ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')

# @app.route('/punchout/session', methods=['GET'])
# def punchout_session():
#     buyer_cookie = request.args.get('buyerCookie')
#     # Create a session for the buyer
#     # Display product catalog
#     return render_template('product_catalog.html', buyer_cookie=buyer_cookie)

#alredy build this function so no testing reuqired
# def send_punchout_order(buyer_cookie, order_details):
#     # Generate POOM XML
#     poom_xml = generate_poom_xml(buyer_cookie, order_details)
#
#     # Send the XML to Ariba
#     url = "https://ariba-network-endpoint.com/poom"
#     headers = {'Content-Type': 'text/xml'}
#     response = requests.post(url, data=poom_xml, headers=headers)
#     return response

