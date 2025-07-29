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
import xml.etree.ElementTree as ET
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import login
import hashlib
from accounts.models import CustomUser

logger = logging.getLogger(__name__)

@csrf_exempt
def setup(request):
    if request.method == 'POST':
        cxml_data = request.body.decode('utf-8')
        logger.info(f"Received cXML PunchOutSetupRequest:\n{cxml_data}")
        root = ET.fromstring(cxml_data)
        
        try:
            buyer_cookie = root.find('.//BuyerCookie').text
            return_url = root.find('.//BrowserFormPost').find('URL').text
            
            # User ki identity (email) cXML se nikalna
            from_identity = root.find('.//Header/From/Credential/Identity').text
            user_email = from_identity if '@' in from_identity else "default@punchoutuser.com"

            # --- AUTOMATIC LOGIN LOGIC START ---
            # Is email se user ko dhoondhein ya naya banayein
            user, created = CustomUser.objects.get_or_create(
                email=user_email,
                defaults={'username': user_email.split('@')[0]} # Zaroori fields ke liye default value
            )

            # User ko system mein login karein
            if user:
                login(request, user)
                logger.info(f"PunchOut user '{user_email}' automatically logged in.")
            # --- AUTOMATIC LOGIN LOGIC END ---

            # Session mein punchout details set karein
            request.session['is_punchout'] = True
            request.session['punchout_buyer_cookie'] = buyer_cookie
            request.session['punchout_return_url'] = return_url
            request.session['punchout_user'] = user_email
            request.session.save()
            
            logger.info(f"PunchOut session created for user: {user_email}")
            return HttpResponseRedirect(reverse('catalog:home'))
            
        except Exception as e:
            logger.error(f"Failed to parse PunchOutSetupRequest: {e}")
            return HttpResponse("Invalid cXML", status=400)
            
    return render(request, 'punchout/setup_form.html')
@csrf_exempt
def punchout_setup(request):
    """Handle PunchOutSetupRequest from Ariba to initiate a shopping session."""
    if request.method != 'POST':
        logger.warning("Invalid method for punchout_setup: %s", request.method)
        return HttpResponse(generate_error_response("Method not allowed"), content_type='text/xml', status=405)

    try:
        posr_xml = request.body.decode('utf-8')
        root = ET.fromstring(posr_xml)

        # Extract necessary fields from PunchOutSetupRequest
        buyer_cookie = root.find(".//BuyerCookie").text
        operation = root.find(".//PunchOutSetupRequest").attrib.get('operation')
        return_url = root.find(".//BrowserFormPost/URL").text
        buyer_identity = root.find(".//From/Credential/Identity").text
        supplier_identity = root.find(".//To/Credential/Identity").text
        shared_secret = root.find(".//Sender/Credential/SharedSecret").text if root.find(".//Sender/Credential/SharedSecret") is not None else None

        # Validate supplier identity and shared secret
        if supplier_identity != settings.PUNCHOUT_ANID:
            logger.error(f"Invalid supplier identity: {supplier_identity}")
            return HttpResponse(generate_error_response("Invalid supplier identity"), content_type='text/xml', status=401)

        if shared_secret and settings.PUNCHOUT_SHARED_SECRET:
            # Validate shared secret (e.g., compare hashed values if applicable)
            hashed_secret = hashlib.sha256(settings.PUNCHOUT_SHARED_SECRET.encode('utf-8')).hexdigest()
            if shared_secret != hashed_secret:
                logger.error("Invalid shared secret")
                return HttpResponse(generate_error_response("Invalid shared secret"), content_type='text/xml', status=401)

        # Initialize or reuse session
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        # Store PunchOut session data
        request.session['is_punchout'] = True
        request.session['punchout_buyer_cookie'] = buyer_cookie
        request.session['punchout_return_url'] = return_url
        request.session['punchout_user'] = buyer_identity
        request.session['operation'] = operation  # Store operation (create, edit, inspect)
        request.session.save()

        # Handle edit/inspect operations (if cart exists)
        if operation in ['edit', 'inspect']:
            cart_items = CartItem.objects.filter(session_key=session_key)
            if not cart_items.exists():
                logger.warning(f"No cart items found for {operation} operation, session_key: {session_key}")
                return HttpResponse(generate_error_response("No cart items for edit/inspect"), content_type='text/xml', status=400)

        # Generate PunchOutSetupResponse with catalog URL
        response = generate_punchout_response(buyer_cookie, buyer_identity, supplier_identity)
        logger.info(f"PunchOutSetupResponse generated for buyer_cookie: {buyer_cookie}, redirecting to catalog")
        return HttpResponse(response, content_type='text/xml')
    except ET.ParseError:
        logger.error("Invalid cXML format in PunchOutSetupRequest")
        return HttpResponse(generate_error_response("Invalid cXML format"), content_type='text/xml', status=400)
    except Exception as e:
        logger.error(f"Error in punchout_setup: {e}")
        return HttpResponse(generate_error_response(str(e)), content_type='text/xml', status=500)

@csrf_exempt
def return_cart_to_ariba(request):
    """Generate PunchOutOrderMessage, save to database, and send to Ariba's return URL."""
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
    header = ET.SubElement(cxml, 'Header')
    from_elem = ET.SubElement(header, 'From')
    ET.SubElement(from_elem, 'Credential', domain="NetworkID").text = buyer_identity
    to_elem = ET.SubElement(header, 'To')
    ET.SubElement(to_elem, 'Credential', domain="DUNS").text = settings.PUNCHOUT_SUPPLIER_DUNS
    sender_elem = ET.SubElement(header, 'Sender')
    sender_cred = ET.SubElement(sender_elem, 'Credential', domain="NetworkID")
    ET.SubElement(sender_cred, 'Identity').text = settings.PUNCHOUT_ANID
    ET.SubElement(sender_cred, 'SharedSecret').text = settings.PUNCHOUT_SHARED_SECRET
    ET.SubElement(sender_elem, 'UserAgent').text = "KalikaEnterprises/1.0"

    message = ET.SubElement(cxml, 'PunchOutOrderMessage')
    ET.SubElement(message, 'BuyerCookie').text = buyer_cookie
    header_message = ET.SubElement(message, 'PunchOutOrderMessageHeader', operationAllowed="create")
    total_elem = ET.SubElement(header_message, 'Total')
    ET.SubElement(total_elem, 'Money', currency="INR").text = str(total)

    for item in cart_items:
        item_in = ET.SubElement(message, 'ItemIn', quantity=str(item.quantity))
        item_id = ET.SubElement(item_in, 'ItemID')
        ET.SubElement(item_id, 'SupplierPartID').text = item.product.item_code
        ET.SubElement(item_id, 'SupplierPartAuxiliaryID').text = str(item.product.item_id)
        item_detail = ET.SubElement(item_in, 'ItemDetail')
        unit_price = ET.SubElement(item_detail, 'UnitPrice')
        ET.SubElement(unit_price, 'Money', currency="INR").text = str(item.product.price)
        ET.SubElement(item_detail, 'Description', **{'xml:lang': 'en'}).text = item.product.product_title
        ET.SubElement(item_detail, 'UnitOfMeasure').text = "EA"
        ET.SubElement(item_detail, 'Classification', domain="UNSPSC").text = item.product.unspsc  # Static UNSPSC code
        if item.product.large_image:
            ET.SubElement(item_detail, 'Extrinsic', name="ImageURL").text = get_s3_presigned_url(
                settings.AWS_S3_BUCKET_NAME, item.product.large_image.lstrip('/')
            )

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

    # Send PunchOutOrderMessage to Ariba's return URL via form POST
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
            request.session['operation'] = None
            request.session.save()
            # Redirect to Ariba for authentication and purchase order confirmation
            return redirect(return_url)
        else:
            logger.error(f"Failed to send PunchOutOrderMessage: {response.status_code} - {response.text}")
            messages.error(request, "Failed to transfer cart to Ariba.")
            return redirect('cart:view_cart')
    except requests.RequestException as e:
        logger.error(f"Error sending PunchOutOrderMessage: {e}")
        messages.error(request, "Error connecting to Ariba.")
        return redirect('cart:view_cart')

def generate_punchout_response(buyer_cookie, buyer_identity, supplier_identity):
    """Generate PunchOutSetupResponse cXML with catalog URL."""
    cxml = ET.Element('cXML', version="1.2.020", payloadID=f"response_{int(datetime.utcnow().timestamp())}",
                     timestamp=datetime.utcnow().isoformat() + 'Z')
    header = ET.SubElement(cxml, 'Header')
    from_elem = ET.SubElement(header, 'From')
    ET.SubElement(from_elem, 'Credential', domain="NetworkID").text = buyer_identity
    to_elem = ET.SubElement(header, 'To')
    ET.SubElement(to_elem, 'Credential', domain="DUNS").text = supplier_identity
    sender_elem = ET.SubElement(header, 'Sender')
    sender_cred = ET.SubElement(sender_elem, 'Credential', domain="NetworkID")
    ET.SubElement(sender_cred, 'Identity').text = settings.PUNCHOUT_ANID
    ET.SubElement(sender_cred, 'SharedSecret').text = settings.PUNCHOUT_SHARED_SECRET
    ET.SubElement(sender_elem, 'UserAgent').text = "KalikaEnterprises/1.0"
    response_elem = ET.SubElement(cxml, 'Response')
    ET.SubElement(response_elem, 'Status', code="200", text="OK")
    punchout_response = ET.SubElement(response_elem, 'PunchOutSetupResponse')
    start_page = ET.SubElement(punchout_response, 'StartPage')
    start_page_url = ET.SubElement(start_page, 'URL')
    start_page_url.text = "https://darkviolet-seal-221814.hostingersite.com/catalog/"
    return ET.tostring(cxml, encoding='utf-8', method='xml').decode('utf-8')

def generate_catalog(request):
    """Generate cXML catalog from Product model for Ariba integration."""
    products = Product.objects.all()
    cxml = ET.Element('cXML', version="1.2.020", payloadID=f"catalog_{int(datetime.utcnow().timestamp())}",
                     timestamp=datetime.utcnow().isoformat() + 'Z')
    message = ET.SubElement(cxml, 'Message')
    punchout_catalog = ET.SubElement(message, 'PunchOutCatalog')
    supplier = ET.SubElement(punchout_catalog, 'Supplier')
    ET.SubElement(supplier, 'SupplierID', domain="NetworkID").text = settings.PUNCHOUT_ANID

    for product in products:
        item = ET.SubElement(punchout_catalog, 'ItemOut')
        ET.SubElement(item, 'SupplierPartID').text = product.item_code
        item_detail = ET.SubElement(item, 'ItemDetail')
        ET.SubElement(item_detail, 'Description', **{'xml:lang': 'en'}).text = product.product_title
        unit_price = ET.SubElement(item_detail, 'UnitPrice')
        ET.SubElement(unit_price, 'Money', currency="INR").text = str(product.price)
        ET.SubElement(item_detail, 'UnitOfMeasure').text = "EA"
        ET.SubElement(item_detail, 'Classification', domain="UNSPSC").text = product.unspsc
        ET.SubElement(item_detail, 'UnitOfMeasure').text=product.unit_of_measure
        if product.large_image:
            ET.SubElement(item_detail, 'Extrinsic', name="ImageURL").text = get_s3_presigned_url(
                settings.AWS_S3_BUCKET_NAME, product.large_image.lstrip('/')
            )

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