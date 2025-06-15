from flask import Blueprint, request, jsonify, session
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

punchout1 = Blueprint('punchout1', __name__)

@punchout1.route('/generate_punchout_order', methods=['POST'])
def generate_punchout_order():
    try:
        # Check session cart
        cart_items = session.get('cart', [])
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty.'}), 400

        # Calculate total
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)

        # Get session data
        buyer_cookie = session.get('buyer_cookie', '123456')
        buyer_identity = session.get('buyer_identity', 'UnknownBuyer')
        supplier_identity = session.get('supplier_identity', '651009354')

        # Generate cXML POOM
        cxml = generate_poom_xml(buyer_cookie, cart_items, total_amount, buyer_identity, supplier_identity)

        # Send to Ariba (replace with actual endpoint)
        ariba_url = "https://ariba-network-endpoint.com/poom"  # Update with Ariba's endpoint
        headers = {'Content-Type': 'text/xml'}
        response = requests.post(ariba_url, data=cxml, headers=headers)

        if response.status_code == 200:
            # Note: Cart is cleared in checkout.py, so no need to clear here
            return jsonify({
                'success': True,
                'redirectURL': 'thankyou.html'
            })
        else:
            print(f"Ariba response error: {response.text}")
            return jsonify({'success': False, 'message': 'Failed to send POOM to Ariba.'}), 500

    except Exception as e:
        print(f"Error in generate_punchout_order: {e}")
        return jsonify({'success': False, 'message': 'Server error.'}), 500

def generate_poom_xml(buyer_cookie, cart_items, total_amount, buyer_identity, supplier_identity):
    # Create cXML root
    cxml = ET.Element('cXML', version="1.2.020", 
                      payloadID=f"poom_{int(datetime.utcnow().timestamp())}",
                      timestamp=datetime.utcnow().isoformat() + 'Z')

    # Header
    header = ET.SubElement(cxml, 'Header')
    from_elem = ET.SubElement(header, 'From')
    credential_from = ET.SubElement(from_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_from, 'Identity').text = buyer_identity

    to_elem = ET.SubElement(header, 'To')
    credential_to = ET.SubElement(to_elem, 'Credential', domain="DUNS")
    ET.SubElement(credential_to, 'Identity').text = supplier_identity

    sender_elem = ET.SubElement(header, 'Sender')
    credential_sender = ET.SubElement(sender_elem, 'Credential', domain="NetworkId")
    ET.SubElement(credential_sender, 'Identity').text = "AN01052123957"
    ET.SubElement(sender_elem, 'UserAgent').text = "YourAppName/1.0"

    # Message
    message = ET.SubElement(cxml, 'Message')
    punchout_order = ET.SubElement(message, 'PunchOutOrderMessage')
    ET.SubElement(punchout_order, 'BuyerCookie').text = buyer_cookie
    header_elem = ET.SubElement(punchout_order, 'PunchOutOrderMessageHeader')
    total_elem = ET.SubElement(header_elem, 'Total')
    money_elem = ET.SubElement(total_elem, 'Money', currency="INR")
    money_elem.text = str(total_amount)

    # Items
    for item in cart_items:
        item_in = ET.SubElement(punchout_order, 'ItemIn', quantity=str(item['quantity']))
        item_id = ET.SubElement(item_in, 'ItemID')
        ET.SubElement(item_id, 'SupplierPartID').text = item.get('code', item['name'])
        item_detail = ET.SubElement(item_in, 'ItemDetail')
        unit_price = ET.SubElement(item_detail, 'UnitPrice')
        money_price = ET.SubElement(unit_price, 'Money', currency="INR")
        money_price.text = str(item['price'])
        ET.SubElement(item_detail, 'Description').text = item['name']

    # Generate XML
    xml_str = ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')
    return f'<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.020/cXML.dtd">{xml_str}'