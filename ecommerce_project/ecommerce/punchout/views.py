from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging
import datetime # datetime import karein

# CartItem aur Product models ko import karein, kyunki yeh Punchout logic mein use ho rahe hain.
# Assuming 'cart' aur 'catalog' apps aapke INSTALLED_APPS mein hain.
from cart.models import CartItem
from catalog.models import Product
from django.contrib import messages
from django.conf import settings # settings ko import karein agar AWS_S3_BUCKET_NAME use ho raha hai

logger = logging.getLogger(__name__)

def generate_punchout_order_cxml(request):
    """
    Punchout order CXML generate karne ke liye view.
    Production mein, Punchout flow supplier ke end par shuru hota hai.
    Yahan hum cart ke items ka use karke CXML banayenge.
    """
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)

    if not cart_items.exists():
        messages.warning(request, "Aapka cart khaali hai, Punchout order generate nahi kiya ja sakta.")
        return redirect('cart:view_cart')

    # CXML document ka root element
    # xmlns attributes ko add karna mahatvapoorn hai
    root = ET.Element("cXML", version="1.2.008", payloadID="{}@punchout-test.com".format(session_key),
                      timestamp="{}".format(datetime.datetime.now().isoformat()),
                      attrib={"xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
                              "xmlns:xml": "http://www.w3.org/XML/1998/namespace"})

    # Header
    header = ET.SubElement(root, "Header")

    # From (Sender's credentials)
    sender = ET.SubElement(header, "From")
    sender_credential = ET.SubElement(sender, "Credential", domain="NetworkID")
    ET.SubElement(sender_credential, "Identity").text = "PunchoutTest" # Aapka Network ID
    ET.SubElement(sender_credential, "SharedSecret").text = "secret" # Aapka Shared Secret

    # To (Receiver's credentials - Supplier)
    receiver = ET.SubElement(header, "To")
    receiver_credential = ET.SubElement(receiver, "Credential", domain="NetworkID")
    ET.SubElement(receiver_credential, "Identity").text = "SupplierNetworkID" # Supplier ka Network ID

    # Sender (User Agent information)
    user_agent_element = ET.SubElement(header, "Sender")
    sender_credential_inner = ET.SubElement(user_agent_element, "Credential", domain="NetworkID")
    ET.SubElement(sender_credential_inner, "Identity").text = "PunchoutTest"
    ET.SubElement(sender_credential_inner, "SharedSecret").text = "secret"
    ET.SubElement(user_agent_element, "UserAgent").text = "DjangoPunchoutTestApp"

    # Request
    request_element = ET.SubElement(root, "Request")
    punchout_order_message = ET.SubElement(request_element, "PunchOutOrderMessage")

    # BuyerCookie (session key ka use kar sakte hain)
    ET.SubElement(punchout_order_message, "BuyerCookie").text = session_key

    # PunchOutOrderMessageHeader
    punchout_order_message_header = ET.SubElement(punchout_order_message, "PunchOutOrderMessageHeader",
                                                  operationAllowed="create")
    ET.SubElement(punchout_order_message_header, "Total", currency="USD").text = str(sum(item.quantity * item.product.price for item in cart_items))
    
    # ShipTo (optional, placeholder values)
    ship_to = ET.SubElement(punchout_order_message_header, "ShipTo")
    address = ET.SubElement(ship_to, "Address", addressID="123")
    ET.SubElement(address, "Name", xml_lang="en").text = "Test Company"
    postal_address = ET.SubElement(address, "PostalAddress")
    ET.SubElement(postal_address, "Street").text = "123 Test Street"
    ET.SubElement(postal_address, "City").text = "Test City"
    ET.SubElement(postal_address, "State").text = "TS"
    ET.SubElement(postal_address, "PostalCode").text = "12345"
    ET.SubElement(postal_address, "Country", isoCountryCode="US").text = "United States"

    # BillTo (optional, placeholder values)
    bill_to = ET.SubElement(punchout_order_message_header, "BillTo")
    address = ET.SubElement(bill_to, "Address", addressID="456")
    ET.SubElement(address, "Name", xml_lang="en").text = "Billing Department"
    postal_address = ET.SubElement(address, "PostalAddress")
    ET.SubElement(postal_address, "Street").text = "456 Billing Ave"
    ET.SubElement(postal_address, "City").text = "Billing City"
    ET.SubElement(postal_address, "State").text = "BS"
    ET.SubElement(postal_address, "PostalCode").text = "67890"
    ET.SubElement(postal_address, "Country", isoCountryCode="US").text = "United States"

    # ItemOut
    item_count = 1
    for item in cart_items:
        item_out = ET.SubElement(punchout_order_message, "ItemOut", quantity=str(item.quantity),
                                  lineNumber=str(item_count), operation="new")
        item_id_element = ET.SubElement(item_out, "ItemID")
        ET.SubElement(item_id_element, "SupplierPartID").text = str(item.product.item_id)
        # Agar aapke paas BuyerPartID hai to use bhi add kar sakte hain
        # ET.SubElement(item_id_element, "BuyerPartID").text = str(item.product.item_id)

        item_detail = ET.SubElement(item_out, "ItemDetail")
        ET.SubElement(item_detail, "UnitPrice").text = str(item.product.price)
        ET.SubElement(item_detail, "Description", xml_lang="en").text = item.product.product_title
        ET.SubElement(item_detail, "UnitOfMeasure").text = "EA" # Each
        ET.SubElement(item_detail, "Classification", domain="UNSPSC").text = "44121706" # Example UNSPSC code
        ET.SubElement(item_detail, "ManufacturerPartID").text = str(item.product.item_id) # Example, if different

        item_count += 1

    # Pretty print the XML
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_cxml = reparsed.toprettyxml(indent="  ")

    # Dummy Punchout Response URL
    # Real-world scenario mein, aap CXML ko ek external Punchout URL par POST karenge.
    # Yahan, hum sirf CXML ko display kar rahe hain aur ek dummy URL par redirect kar rahe hain.
    
    # Store CXML and other info in session for debugging
    request.session['punchout_cxml_data'] = pretty_cxml
    request.session['punchout_request_url'] = "http://punchout-supplier.com/punchout/process" # Dummy URL
    request.session['punchout_response_url'] = "http://your-website.com/punchout/punchout-return/" # Dummy return URL

    logger.info(f"Punchout CXML generate kiya gaya, session_key: {session_key}")
    return redirect('punchout:show_punchout_debug')

def show_punchout_debug(request):
    """
    Punchout debug information display karne ke liye view
    """
    cxml_data = request.session.get('punchout_cxml_data', 'Koi CXML data nahi mila.')
    request_url = request.session.get('punchout_request_url', 'Koi request URL nahi mila.')
    response_url = request.session.get('punchout_response_url', 'Koi response URL nahi mila.')

    # Ek baar dikhane ke baad session se data hata den
    if 'punchout_cxml_data' in request.session:
        del request.session['punchout_cxml_data']
    if 'punchout_request_url' in request.session:
        del request.session['punchout_request_url']
    if 'punchout_response_url' in request.session:
        del request.session['punchout_response_url']

    context = {
        'cxml_data': cxml_data,
        'punchout_request_url': request_url,
        'punchout_response_url': response_url,
    }
    return render(request, 'punchout/punchout_debug.html', context)

# Agar aapko Punchout setup request handling bhi karni hai, to aap iske liye bhi views add kar sakte hain.
# Jaise ki:
# def punchout_setup_request(request):
#     if request.method == 'POST':
#         cxml_data = request.body.decode('utf-8')
#         # Yahan CXML parse karein aur session mein store karein Punchout details (e.g., return URL)
#         # Phir user ko product catalog par redirect karein
#         return HttpResponse("Punchout Setup Request Received", status=200)
#     return HttpResponse("Invalid Punchout Setup Request", status=400)
