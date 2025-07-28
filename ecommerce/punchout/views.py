# punchout/views.py
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from cart.models import CartItem
from catalog.models import Product
from catalog.views import get_s3_presigned_url
import requests
from django.contrib import messages
from .models import PunchOutOrder
import uuid

logger = logging.getLogger(__name__)

@csrf_exempt
def punchout_setup(request):
    """Handle PunchOutSetupRequest and return PunchOutSetupResponse."""
    if request.method == 'POST':
        try:
            posr_xml = request.body.decode('utf-8')
            root = ET.fromstring(posr_xml)

            # Extract necessary fields
            buyer_cookie = root.find(".//BuyerCookie").text
            operation = root.find(".//PunchOutSetupRequest").attrib.get('operation')
            return_url = root.find(".//BrowserFormPost/URL").text
            buyer_identity = root.find(".//From/Credential/Identity").text
            supplier_identity = root.find(".//To/Credential/Identity").text

            # Validate credentials
            if supplier_identity != settings.PUNCHOUT_ANID:
                logger.error(f"Invalid supplier identity: {supplier_identity}")
                return HttpResponse(generate_error_response("Invalid supplier identity"), content_type='text/xml', status=401)

            # Store PunchOut session data
            if not request.session.session_key:
                request.session.create()
            request.session['is_punchout'] = True
            request.session['punchout_buyer_cookie'] = buyer_cookie
            request.session['punchout_return_url'] = return_url
            request.session['punchout_user'] = buyer_identity
            request.session.save()

            # Generate PunchOutSetupResponse
            response = generate_punchout_response(buyer_cookie, buyer_identity, supplier_identity)
            logger.info(f"PunchOutSetupResponse generated for buyer_cookie: {buyer_cookie}")
            return HttpResponse(response, content_type='text/xml')
        except ET.ParseError:
            logger.error("Invalid cXML format in PunchOutSetupRequest")
            return HttpResponse(generate_error_response("Invalid cXML format"), content_type='text/xml', status=400)
        except Exception as e:
            logger.error(f"Error in punchout_setup: {e}")
            return HttpResponse(generate_error_response(str(e)), content_type='text/xml', status=500)
    return HttpResponse(generate_error_response("Method not allowed"), content_type='text/xml', status=405)

@csrf_exempt
def return_cart_to_ariba(request):
    """Generate PunchOutOrderMessage, save to database with cXML, and send to Ariba's return URL."""
    if request.method != 'POST':
        logger.warning("Invalid method for return_cart_to_ariba: %s", request.method)
        return HttpResponse(generate_error_response("Method not allowed"), content_type='text/xml', status=405)

    if not request.session.get('is_punchout', False):
        logger.warning("Non-PunchOut session attempted to access return_cart_to_ariba")
        messages.warning(request, "This is not a valid PunchOut session.")
        return redirect('cart:view_cart')

    session_key = request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)
    if not cart_items.exists():
        logger.warning("Empty cart for PunchOut session")
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:view_cart')

    buyer_cookie = request.session.get('punchout_buyer_cookie', '123456')
    return_url = request.session.get('punchout_return_url', settings.PUNCHOUT_RETURN_URL)
    buyer_identity = request.session.get('punchout_user', 'test@localhost')
    total = sum(item.quantity * item.product.price for item in cart_items)

    # Generate unique order_id
    order_id = uuid.uuid4()

    # Generate PunchOutOrderMessage
    cxml = ET.Element('cXML', version="1.2.020", payloadID=f"poom_{session_key}_{int(datetime.utcnow().timestamp())}",
                     timestamp=datetime.utcnow().isoformat() + 'Z')
    message = ET.SubElement(cxml, 'PunchOutOrderMessage')
    ET.SubElement(message, 'BuyerCookie').text = buyer_cookie
    header = ET.SubElement(message, 'PunchOutOrderMessageHeader')
    total_elem = ET.SubElement(header, 'Total')
    ET.SubElement(total_elem, 'Money', currency="INR").text = str(total)

    for item in cart_items:
        item_in = ET.SubElement(message, 'ItemIn', quantity=str(item.quantity))
        item_id = ET.SubElement(item_in, 'ItemID')
        ET.SubElement(item_id, 'SupplierPartID').text = item.product.item_code
        item_detail = ET.SubElement(item_in, 'ItemDetail')
        unit_price = ET.SubElement(item_detail, 'UnitPrice')
        ET.SubElement(unit_price, 'Money', currency="INR").text = str(item.product.price)
        ET.SubElement(item_detail, 'Description').text = item.product.product_title
        ET.SubElement(item_detail, 'UnitOfMeasure').text = "EA"

    poom_xml = ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')

    # Save cart items to PunchOutOrder with cXML
    for item in cart_items:
        PunchOutOrder.objects.create(
            order_id=order_id,
            session_key=session_key,
            buyer_cookie=buyer_cookie,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
            return_url=return_url,
            buyer_identity=buyer_identity,
            cxml_content=poom_xml
        )
    logger.info(f"Saved {cart_items.count()} items to PunchOutOrder with order_id: {order_id}, session_key: {session_key}")

    # Send to Ariba's return URL
    try:
        response = requests.post(return_url, data=poom_xml, headers={'Content-Type': 'text/xml'})
        if response.status_code == 200:
            logger.info(f"PunchOutOrderMessage sent successfully to {return_url}")
            # Clear cart and session
            cart_items.delete()
            request.session['is_punchout'] = False
            request.session['punchout_buyer_cookie'] = None
            request.session['punchout_return_url'] = None
            request.session['punchout_user'] = None
            request.session.save()
            return redirect(return_url)
        else:
            logger.error(f"Failed to send PunchOutOrderMessage: {response.status_code}")
            messages.error(request, "Failed to transfer cart to Ariba.")
            return redirect('cart:view_cart')
    except requests.RequestException as e:
        logger.error(f"Error sending PunchOutOrderMessage: {e}")
        messages.error(request, "Error connecting to Ariba.")
        return redirect('cart:view_cart')

def generate_punchout_response(buyer_cookie, buyer_identity, supplier_identity):
    """Generate PunchOutSetupResponse cXML."""
    cxml = ET.Element('cXML', version="1.2.020", payloadID=f"response_{int(datetime.utcnow().timestamp())}",
                     timestamp=datetime.utcnow().isoformat() + 'Z')
    header = ET.SubElement(cxml, 'Header')
    from_elem = ET.SubElement(header, 'From')
    credential_from = ET.SubElement(from_elem, 'Credential', domain="NetworkID")
    ET.SubElement(credential_from, 'Identity').text = buyer_identity
    to_elem = ET.SubElement(header, 'To')
    credential_to = ET.SubElement(to_elem, 'Credential', domain="NetworkID")
    ET.SubElement(credential_to, 'Identity').text = supplier_identity
    sender_elem = ET.SubElement(header, 'Sender')
    credential_sender = ET.SubElement(sender_elem, 'Credential', domain="NetworkID")
    ET.SubElement(credential_sender, 'Identity').text = settings.PUNCHOUT_ANID
    ET.SubElement(sender_elem, 'UserAgent').text = "KalikaEnterprises/1.0"
    response_elem = ET.SubElement(cxml, 'Response')
    status_elem = ET.SubElement(response_elem, 'Status', code="200", text="OK")
    punchout_response = ET.SubElement(response_elem, 'PunchOutSetupResponse')
    start_page = ET.SubElement(punchout_response, 'StartPage')
    start_page_url = ET.SubElement(start_page, 'URL')
    start_page_url.text = "https://darkviolet-seal-221814.hostingersite.com/catalog/"
    return ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')

def generate_catalog(request):
    """Generate cXML catalog from Product model and Excel data."""
    products = Product.objects.all()
    cxml = ET.Element('cXML', version="1.2.020", payloadID=f"catalog_{int(datetime.utcnow().timestamp())}",
                     timestamp=datetime.utcnow().isoformat() + 'Z')
    catalog = ET.SubElement(cxml, 'Message')
    punchout_catalog = ET.SubElement(catalog, 'PunchOutCatalog')
    supplier = ET.SubElement(punchout_catalog, 'Supplier')
    ET.SubElement(supplier, 'SupplierID', domain="NetworkID").text = settings.PUNCHOUT_ANID

    # Add sample item from Excel file
    item = ET.SubElement(punchout_catalog, 'ItemOut')
    ET.SubElement(item, 'SupplierPartID').text = "415263"
    item_detail = ET.SubElement(item, 'ItemDetail')
    ET.SubElement(item_detail, 'Description').text = "KALIKA ENTERPRISES"
    unit_price = ET.SubElement(item_detail, 'UnitPrice')
    ET.SubElement(unit_price, 'Money', currency="INR").text = "1"
    ET.SubElement(item_detail, 'UNSPSC').text = "2711"
    ET.SubElement(item_detail, 'UnitOfMeasure').text = "EA"

    # Add dynamic products from Product model
    for product in products:
        item = ET.SubElement(punchout_catalog, 'ItemOut')
        ET.SubElement(item, 'SupplierPartID').text = product.item_code
        item_detail = ET.SubElement(item, 'ItemDetail')
        ET.SubElement(item_detail, 'Description').text = product.product_title
        unit_price = ET.SubElement(item_detail, 'UnitPrice')
        ET.SubElement(unit_price, 'Money', currency="INR").text = str(product.price)
        ET.SubElement(item_detail, 'UNSPSC').text = "2711"
        ET.SubElement(item_detail, 'UnitOfMeasure').text = "EA"

    xml_str = ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')
    return HttpResponse(xml_str, content_type='text/xml')

def generate_error_response(message):
    """Generate error cXML response."""
    cxml = ET.Element('cXML', version="1.2.020", payloadID=f"error_{int(datetime.utcnow().timestamp())}",
                     timestamp=datetime.utcnow().isoformat() + 'Z')
    response = ET.SubElement(cxml, 'Response')
    status = ET.SubElement(response, 'Status', code="400", text="Bad Request")
    status.text = message
    return ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')