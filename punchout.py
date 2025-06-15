from flask import Blueprint, request, Response, session
import xml.etree.ElementTree as ET
from datetime import datetime

check = Blueprint('check', __name__)

@check.route('/punchout/setup', methods=['POST'])
def punchout_setup():
    try:
        # Parse incoming cXML from Ariba
        posr_xml = request.data.decode('utf-8')
        root = ET.fromstring(posr_xml)

        # Extract required fields
        buyer_cookie = root.find(".//BuyerCookie").text
        buyer_identity = root.find(".//From/Credential/Identity").text
        supplier_identity = root.find(".//To/Credential/Identity").text

        # Store in session for POOM
        session['buyer_cookie'] = buyer_cookie
        session['buyer_identity'] = buyer_identity
        session['supplier_identity'] = supplier_identity
        session.modified = True

        # Generate cXML response
        response = generate_punchout_response({
            'buyer_cookie': buyer_cookie,
            'buyer_identity': buyer_identity,
            'supplier_identity': supplier_identity
        })

        return Response(response, content_type='text/xml')

    except ET.ParseError:
        return Response("<cXML><Response><Status code='400' text='Invalid cXML'/></Response></cXML>", 
                        content_type='text/xml', status=400)
    except Exception as e:
        print(f"Error in punchout_setup: {e}")
        return Response("<cXML><Response><Status code='500' text='Server Error'/></Response></cXML>", 
                        content_type='text/xml', status=500)

def generate_punchout_response(user_data):
    # Create cXML root
    cxml = ET.Element('cXML', version="1.2.020", 
                      payloadID=f"response_{int(datetime.utcnow().timestamp())}",
                      timestamp=datetime.utcnow().isoformat() + 'Z')

    # Header
    header = ET.SubElement(cxml, 'Header')
    from_elem = ET.SubElement(header, 'From')
    credential_from = ET.SubElement(from_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_from, 'Identity').text = user_data.get('buyer_identity', 'UnknownBuyer')

    to_elem = ET.SubElement(header, 'To')
    credential_to = ET.SubElement(to_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_to, 'Identity').text = "651009354"  # Supplier DUNS

    sender_elem = ET.SubElement(header, 'Sender')
    credential_sender = ET.SubElement(sender_elem, 'Credential', domain="NetworkId")
    ET.SubElement(credential_sender, 'Identity').text = "AN01052123957"  # Supplier ANID
    ET.SubElement(sender_elem, 'UserAgent').text = "YourAppName/1.0"

    # Response
    response_elem = ET.SubElement(cxml, 'Response')
    status_elem = ET.SubElement(response_elem, 'Status', code="200", text="OK")
    punchout_response = ET.SubElement(response_elem, 'PunchOutSetupResponse')
    start_page = ET.SubElement(punchout_response, 'StartPage')
    start_page_url = ET.SubElement(start_page, 'URL')
    start_page_url.text = "https://darkviolet-seal-221814.hostingersite.com/cart"

    # Generate XML
    xml_str = ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')
    return f'<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.020/cXML.dtd">{xml_str}'