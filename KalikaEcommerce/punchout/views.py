# punchout/views.py

import xml.etree.ElementTree as ET
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

# --- FIX #1: Correctly import CartItem instead of Cart ---
from cart.models import CartItem
# --- This was the source of the error ---
from catalog.models import Product  # Make sure Product is imported to use it in queries

# These are credentials you and the buyer (Ariba user) agree on beforehand.
PUNCHOUT_CREDENTIALS = {
    'domain': 'NetworkID',
    'identity': 'AN0123456789',
    'secret': 'very-secret-password'
}


# --- FIX #2: Implement the helper function to get cart items ---
def get_user_cart_items(request):
    """
    Retrieves all CartItem objects associated with the current
    user's PunchOut session.
    """
    if request.session.get('is_punchout', False):
        # In a PunchOut session, we identify the user by an extrinsic value
        # we stored, like their email. For this to work, you would need
        # a way to link the punchout_user to your cart items.
        # A simpler way for now is to use the session key.
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        return CartItem.objects.filter(session_key=session_key)
    return CartItem.objects.none()  # Return an empty queryset if not a punchout session


@csrf_exempt
def punchout_setup(request):
    if request.method == 'POST':
        cxml_payload = request.body.decode('utf-8')
        try:
            root = ET.fromstring(cxml_payload)
            # --- 1. Parse the cXML ---
            header = root.find('.//Header')
            sender_identity = header.find('.//Sender/Credential/Identity').text
            sender_secret = header.find('.//Sender/Credential/SharedSecret').text

            # --- 2. Authenticate ---
            if (sender_identity != PUNCHOUT_CREDENTIALS['identity'] or
                    sender_secret != PUNCHOUT_CREDENTIALS['secret']):
                return HttpResponse("Authentication failed", status=401)

            # --- 3. Store info in session ---
            browser_post_url = root.find('.//BrowserFormPost/URL').text
            request.session['is_punchout'] = True
            request.session['punchout_return_url'] = browser_post_url

            # Ensure a session key exists to link the cart items to
            if not request.session.session_key:
                request.session.create()

            user_email = root.find('.//Extrinsic[@name="UserEmail"]').text
            request.session['punchout_user'] = user_email
            print(f"PunchOut session started for {user_email}")

            # --- 4. Redirect to catalog ---
            return HttpResponseRedirect(reverse('catalog:product-list'))  # Make sure this URL name is correct
        except ET.ParseError as e:
            return HttpResponse(f"Invalid cXML format: {e}", status=400)

    return HttpResponse("This URL only accepts POST requests.", status=405)


def return_cart_to_ariba(request):
    if not request.session.get('is_punchout', False):
        return HttpResponse("This is not a valid PunchOut session.", status=400)

    return_url = request.session.get('punchout_return_url')
    cart_items = get_user_cart_items(request)

    if not return_url or not cart_items:
        return HttpResponse("Your cart is empty or the session has expired.", status=400)

    # --- 2. Build the cXML PunchOutOrderMessage ---
    cxml = ET.Element('cXML', payloadID=f"order-{now().timestamp()}", timestamp=now().isoformat())
    header = ET.SubElement(cxml, 'Header')
    # You would fill in From, To, Sender credentials here

    message = ET.SubElement(cxml, 'Message')
    punchout_order_message = ET.SubElement(message, 'PunchOutOrderMessage')

    buyer_cookie_elem = ET.SubElement(punchout_order_message, 'BuyerCookie')
    buyer_cookie_elem.text = "Rcvd_Cookie_12345"  # This should be the cookie from the setup request

    for item in cart_items:
        # Use a try-except block in case a product was deleted
        try:
            item_in = ET.SubElement(punchout_order_message, 'ItemIn', quantity=str(item.quantity))
            item_id = ET.SubElement(item_in, 'ItemID')

            # Using Item_Code from your product data
            supplier_part_id = ET.SubElement(item_id, 'SupplierPartID')
            supplier_part_id.text = item.product.Item_Code

            item_detail = ET.SubElement(item_in, 'ItemDetail')
            unit_price = ET.SubElement(item_detail, 'UnitPrice')
            money = ET.SubElement(unit_price, 'Money', currency='INR')
            money.text = str(item.product.Price)

            description = ET.SubElement(item_detail, 'Description', {'xml:lang': 'en'})
            description.text = item.product.Product_Title  # Using Product_Title

            uom = ET.SubElement(item_detail, 'UnitOfMeasure')
            uom.text = 'EA'  # Each (or other appropriate unit)

        except Product.DoesNotExist:
            continue  # Skip items where the product has been removed from the database

    cxml_string = ET.tostring(cxml, encoding='UTF-8').decode('UTF-8')

    context = {
        'return_url': return_url,
        'cxml_cart': cxml_string
    }
    return render(request, 'punchout/return_to_ariba.html', context)