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
        # Generate PunchOut Setup Response (POSR)
        response = generate_punchout_response(user_data)
        return response  # Return XML response


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