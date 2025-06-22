import xml.etree.ElementTree as ET
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from cart.models import CartItem
from catalog.models import Product
import logging

logger = logging.getLogger(__name__)

PUNCHOUT_CREDENTIALS = {
    'domain': 'NetworkID',
    'identity': 'AN0123456789',
    'secret': 'very-secret-password'
}

def get_user_cart_items(request):
    if request.session.get('is_punchout', False):
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart_items = CartItem.objects.filter(session_key=session_key)
        logger.info(f"Retrieved {cart_items.count()} cart items for session {session_key}")
        return cart_items
    logger.info("No PunchOut session, returning empty cart")
    return CartItem.objects.none()

@csrf_exempt
def punchout_setup(request):
    if request.method == 'POST':
        cxml_payload = request.body.decode('utf-8')
        logger.info(f"Received cXML: {cxml_payload}")
        try:
            root = ET.fromstring(cxml_payload)
            header = root.find('.//Header')
            sender_identity = header.find('.//Sender/Credential/Identity').text
            sender_secret = header.find('.//Sender/Credential/SharedSecret').text

            if (sender_identity != PUNCHOUT_CREDENTIALS['identity'] or
                    sender_secret != PUNCHOUT_CREDENTIALS['secret']):
                logger.error("Authentication failed")
                return HttpResponse("Authentication failed", status=401)

            browser_post_url = root.find('.//BrowserFormPost/URL').text
            request.session['is_punchout'] = True
            request.session['punchout_return_url'] = browser_post_url
            request.session.modified = True

            if not request.session.session_key:
                request.session.create()
            
            user_email = root.find('.//Extrinsic[@name="UserEmail"]').text
            request.session['punchout_user'] = user_email
            request.session.modified = True
            logger.info(f"PunchOut session started for {user_email}, session: {request.session.session_key}, "
                        f"return_url: {browser_post_url}")
            
            return render(request, 'punchout/punchout_request.html', {'request_xml': cxml_payload})
        except ET.ParseError as e:
            logger.error(f"Invalid cXML format: {e}")
            return HttpResponse(f"Invalid cXML format: {e}", status=400)
        except Exception as e:
            logger.error(f"Unexpected error in punchout_setup: {e}")
            return HttpResponse(f"Server error: {e}", status=500)

    logger.info("Non-POST request to punchout_setup")
    return HttpResponse("This URL only accepts POST requests.", status=405)

def test_punchout_session(request):
    request.session['is_punchout'] = True
    request.session['punchout_return_url'] = 'http://127.0.0.1:8000/punchout/response/'
    request.session['punchout_user'] = 'test@localhost'
    request.session.modified = True
    if not request.session.session_key:
        request.session.create()
    logger.info(f"Test PunchOut session created: {request.session.session_key}, "
                f"return_url: {request.session.get('punchout_return_url')}")
    return redirect('catalog:product_list')

def debug_session(request):
    session_data = {
        'session_key': request.session.session_key,
        'is_punchout': request.session.get('is_punchout', False),
        'punchout_return_url': request.session.get('punchout_return_url', 'Not set'),
        'punchout_user': request.session.get('punchout_user', 'Not set')
    }
    logger.info(f"Session debug: {session_data}")
    return HttpResponse(f"Session Data: {session_data}")

def return_cart_to_ariba(request):
    session_key = request.session.session_key
    is_punchout = request.session.get('is_punchout', False)
    logger.info(f"Accessing return_to_ariba, session: {session_key}, is_punchout: {is_punchout}")
    
    if not is_punchout:
        logger.error(f"Not a valid PunchOut session for {session_key}")
        return HttpResponse("This is not a valid PunchOut session.", status=400)

    return_url = request.session.get('punchout_return_url')
    cart_items = get_user_cart_items(request)

    if not return_url or not cart_items:
        logger.error(f"Empty cart or missing return URL for {session_key}")
        return HttpResponse("Your cart is empty or the session has expired.", status=400)

    cxml = ET.Element('cXML', payloadID=f"order-{now().timestamp()}", timestamp=now().isoformat())
    header = ET.SubElement(cxml, 'Header')
    message = ET.SubElement(cxml, 'Message')
    punchout_order_message = ET.SubElement(message, 'PunchOutOrderMessage')

    buyer_cookie_elem = ET.SubElement(punchout_order_message, 'BuyerCookie')
    buyer_cookie_elem.text = "Rcvd_Cookie_12345"

    for item in cart_items:
        try:
            item_in = ET.SubElement(punchout_order_message, 'ItemIn', quantity=str(item.quantity))
            item_id = ET.SubElement(item_in, 'ItemID')
            supplier_part_id = ET.SubElement(item_id, 'SupplierPartID')
            supplier_part_id.text = item.product.item_code

            item_detail = ET.SubElement(item_in, 'ItemDetail')
            unit_price = ET.SubElement(item_detail, 'UnitPrice')
            money = ET.SubElement(unit_price, 'Money', currency='INR')
            money.text = str(item.product.price)

            description = ET.SubElement(item_detail, 'Description', {'xml:lang': 'en'})
            description.text = item.product.product_title

            uom = ET.SubElement(item_detail, 'UnitOfMeasure')
            uom.text = 'EA'
        except Product.DoesNotExist:
            logger.warning(f"Product missing for cart item in session {session_key}")
            continue

    cxml_string = ET.tostring(cxml, encoding='UTF-8').decode('UTF-8')
    logger.info(f"Generated cXML for session {session_key}: {cxml_string}")

    context = {
        'return_url': return_url,
        'cxml_cart': cxml_string
    }
    return render(request, 'punchout/punchout_order.html', context)

def punchout_response(request):
    if request.method == 'POST':
        cxml_received = request.POST.get('cxml-urlencoded', 'No cXML received')
        logger.info(f"PunchOut response received: {cxml_received}")
        return render(request, 'punchout/punchout_response.html', {'response_cxml': cxml_received, 'return_url': request.session.get('punchout_return_url')})
    # Allow GET for debugging, showing a message
    logger.info(f"GET request to punchout_response, no data submitted")
    return render(request, 'punchout/punchout_response.html', {'response_cxml': 'No cXML submitted (GET request)', 'return_url': request.session.get('punchout_return_url', 'Not set')})