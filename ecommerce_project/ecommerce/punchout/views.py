import xml.etree.ElementTree as ET
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from cart.models import CartItem
from catalog.models import Product
import logging

logger = logging.getLogger(__name__)

PUNCHOUT_CREDENTIALS = {
    'domain': 'NetworkID',
    'identity': 'AN00012345678',  # Matches ARIBA_NETWORK_ID from settings
    'secret': 'very-secret-password'  # Replace with secure credential
}

def get_user_cart_items(request):
    if request.session.get('is_punchout', False):
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        return CartItem.objects.filter(session_key=session_key)
    return CartItem.objects.none()

@csrf_exempt
def punchout_setup(request):
    if request.method == 'POST':
        try:
            cxml_payload = request.body.decode('utf-8')
            logger.info(f"Received cXML payload: {cxml_payload}")
            root = ET.fromstring(cxml_payload)
            header = root.find('.//Header')
            sender_identity = header.find('.//Sender/Credential/Identity').text
            sender_secret = header.find('.//Sender/Credential/SharedSecret').text

            # Authenticate (uncomment in production with secure credentials)
            # if (sender_identity != PUNCHOUT_CREDENTIALS['identity'] or
            #         sender_secret != PUNCHOUT_CREDENTIALS['secret']):
            #     logger.error("Authentication failed")
            #     return HttpResponse("Authentication failed", status=401)

            browser_post_url = root.find('.//BrowserFormPost/URL').text
            user_email = root.find('.//Extrinsic[@name="UserEmail"]').text or 'test@localhost'
            request.session['is_punchout'] = True
            request.session['punchout_return_url'] = browser_post_url
            request.session['punchout_user'] = user_email
            request.session['buyer_cookie'] = root.find('.//BuyerCookie').text or 'Rcvd_Cookie_12345'

            if not request.session.session_key:
                request.session.create()
            logger.info(f"PunchOut session started for {user_email}, session_key: {request.session.session_key}")
            return HttpResponseRedirect(reverse('catalog:home'))
        except ET.ParseError as e:
            logger.error(f"Invalid cXML format: {e}")
            return HttpResponse(f"Invalid cXML format: {e}", status=400)
        except Exception as e:
            logger.error(f"Error in punchout_setup: {e}")
            return HttpResponse(f"Error processing request: {e}", status=500)
    return HttpResponse("This URL only accepts POST requests.", status=405)

@csrf_exempt
def return_cart_to_ariba(request):
    if not request.session.get('is_punchout', False):
        logger.warning("Not a valid PunchOut session")
        return HttpResponse("This is not a valid PunchOut session.", status=400)

    return_url = request.session.get('punchout_return_url')
    cart_items = get_user_cart_items(request)

    if not return_url or not cart_items:
        logger.warning("Cart empty or session expired")
        return HttpResponse("Your cart is empty or the session has expired.", status=400)

    cxml = ET.Element('cXML', payloadID=f"order-{now().timestamp()}", timestamp=now().isoformat(), version="1.2.014", xml_lang="en-US")
    header = ET.SubElement(cxml, 'Header')
    from_cred = ET.SubElement(header, 'From')
    from_identity = ET.SubElement(from_cred, 'Credential', domain='NetworkID')
    ET.SubElement(from_identity, 'Identity').text = PUNCHOUT_CREDENTIALS['identity']
    to_cred = ET.SubElement(header, 'To')
    to_identity = ET.SubElement(to_cred, 'Credential', domain='NetworkID')
    ET.SubElement(to_identity, 'Identity').text = 'AN09067477712'  # Buyer's NetworkID
    sender = ET.SubElement(header, 'Sender')
    sender_cred = ET.SubElement(sender, 'Credential', domain='NetworkID')
    ET.SubElement(sender_cred, 'Identity').text = PUNCHOUT_CREDENTIALS['identity']
    ET.SubElement(sender_cred, 'SharedSecret').text = PUNCHOUT_CREDENTIALS['secret']

    message = ET.SubElement(cxml, 'Message')
    punchout_order_message = ET.SubElement(message, 'PunchOutOrderMessage')
    ET.SubElement(punchout_order_message, 'BuyerCookie').text = request.session.get('buyer_cookie', 'Rcvd_Cookie_12345')

    total = ET.SubElement(punchout_order_message, 'Total')
    money = ET.SubElement(total, 'Money', currency='INR')
    money.text = str(sum(item.quantity * item.product.price for item in cart_items))

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
            classification = ET.SubElement(item_detail, 'Classification', domain='UNSPSC')
            classification.text = '43191504'  # Default UNSPSC code
        except Product.DoesNotExist:
            logger.warning(f"Product {item.product_id} not found, skipping")
            continue

    cxml_string = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.014/cXML.dtd">' + ET.tostring(cxml, encoding='unicode')
    
    context = {
        'return_url': return_url,
        'cxml_cart': cxml_string
    }
    logger.info(f"PunchOut cXML generated: {cxml_string}")
    return render(request, 'punchout/return_to_ariba.html', context)

@csrf_exempt
def show_punchout_debug(request):
    cart_items = get_user_cart_items(request)
    return_url = request.session.get('punchout_return_url', 'N/A')
    cxml_response = None

    if request.method == 'POST':
        if not request.session.get('is_punchout', False):
            logger.warning("Not a valid PunchOut session in debug")
            return render(request, 'punchout/debug.html', {
                'cart_items': cart_items,
                'return_url': return_url,
                'cxml_response': None,
                'error': "Not a valid PunchOut session."
            })

        if not cart_items:
            logger.warning("Cart empty in debug")
            return render(request, 'punchout/debug.html', {
                'cart_items': cart_items,
                'return_url': return_url,
                'cxml_response': None,
                'error': "Cart is empty."
            })

        # Generate cXML directly (similar to return_cart_to_ariba)
        cxml = ET.Element('cXML', payloadID=f"order-{now().timestamp()}", timestamp=now().isoformat(), version="1.2.014", xml_lang="en-US")
        header = ET.SubElement(cxml, 'Header')
        from_cred = ET.SubElement(header, 'From')
        from_identity = ET.SubElement(from_cred, 'Credential', domain='NetworkID')
        ET.SubElement(from_identity, 'Identity').text = PUNCHOUT_CREDENTIALS['identity']
        to_cred = ET.SubElement(header, 'To')
        to_identity = ET.SubElement(to_cred, 'Credential', domain='NetworkID')
        ET.SubElement(to_identity, 'Identity').text = 'AN09067477712'  # Buyer's NetworkID
        sender = ET.SubElement(header, 'Sender')
        sender_cred = ET.SubElement(sender, 'Credential', domain='NetworkID')
        ET.SubElement(sender_cred, 'Identity').text = PUNCHOUT_CREDENTIALS['identity']
        ET.SubElement(sender_cred, 'SharedSecret').text = PUNCHOUT_CREDENTIALS['secret']

        message = ET.SubElement(cxml, 'Message')
        punchout_order_message = ET.SubElement(message, 'PunchOutOrderMessage')
        ET.SubElement(punchout_order_message, 'BuyerCookie').text = request.session.get('buyer_cookie', 'Rcvd_Cookie_12345')

        total = ET.SubElement(punchout_order_message, 'Total')
        money = ET.SubElement(total, 'Money', currency='INR')
        money.text = str(sum(item.quantity * item.product.price for item in cart_items))

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
                classification = ET.SubElement(item_detail, 'Classification', domain='UNSPSC')
                classification.text = '43191504'  # Default UNSPSC code
            except Product.DoesNotExist:
                logger.warning(f"Product {item.product_id} not found, skipping")
                continue

        cxml_response = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.014/cXML.dtd">' + ET.tostring(cxml, encoding='unicode')
        logger.info(f"Debug cXML generated: {cxml_response}")

    return render(request, 'punchout/debug.html', {
        'cart_items': cart_items,
        'return_url': return_url,
        'cxml_response': cxml_response
    })