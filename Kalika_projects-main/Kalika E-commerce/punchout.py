from flask import Blueprint, render_template
from flask import Flask, request, jsonify, session
import os

<<<<<<< Updated upstream
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
=======
app = Flask(__name__)
>>>>>>> Stashed changes


punchout1 = Blueprint('punchout1', __name__)

url = 'http://127.0.0.1:5000/generate_punchout_order'
#
# # Prepare the cart data
# cart_data = {
#     "cartItems": [
#         {"name": "{{item.name}}", "quantity": "{{item.quantity}}", "price": "{{item.price}}"},
#         {"name": "Item 2", "quantity": 1, "price": 700}
#     ],
#     "totalAmount": 1700
# }

# Send the POST request
# response = requests.post(url, json=cart_data)
# Route to handle PunchOutOrderMessage generation

@punchout1.route('/generate_punchout_order', methods=['POST'])
def generate_punchout_order():
    # Read JSON input (sent from the checkout button)
    cart_data = request.get_json()

    print(cart_data)
    # Validate cart data
    if not cart_data or 'cartItems' not in cart_data or 'totalAmount' not in cart_data:
        return jsonify({'success': False, 'message': 'Invalid cart data.'}), 400

    # Extract cart data
    cart_items = cart_data['cartItems']
    total_amount = cart_data['totalAmount']


    # Prepare cXML PunchOutOrderMessage
    buyer_cookie = '123456'  # Unique identifier for the PunchOut session
    punchout_order_message = f"""<PunchOutOrderMessage>
    <BuyerCookie>{buyer_cookie}</BuyerCookie>
    <PunchOutOrderMessageHeader>
        <Total>
            <Money currency="INR">{total_amount}</Money>
        </Total>
    </PunchOutOrderMessageHeader>"""

    # Add each item to the cXML message
    for item in cart_items:
        punchout_order_message += f"""
    <ItemIn quantity="{item['quantity']}">
        <ItemID>
            <SupplierPartID>{item['name']}</SupplierPartID>
        </ItemID>
        <ItemDetail>
            <UnitPrice>
                <Money currency="INR">{item['price']}</Money>
            </UnitPrice>
        </ItemDetail>
    </ItemIn>"""

    # Close the PunchOutOrderMessage
    punchout_order_message += "</PunchOutOrderMessage>"

    # Simulate saving the PunchOutOrderMessage (or it could be sent to a server)
    with open('punchout_order.xml', 'w') as file:
        file.write(punchout_order_message)

    session.pop('cart', None)
    print("session",session)
    # Respond with success and redirect URL
    return jsonify({
        'success': True,
        'redirectURL': 'thankyou.html'  # Redirect to a thank-you page after submission
    })


if __name__ == '__main__':
    app.run(debug=True)



