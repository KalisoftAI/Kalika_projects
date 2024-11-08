# from flask import Flask, Response

# app = Flask(__name__)

# # Function to generate the CXML response
# def generate_cxml():
#     # Sample cart data
#     cart = [
#         # {'name': '{item.name}', 'price': '{item.price}', 'quantity': '{item.quantity}'},
#         {'name': item_name, 'price': item_price, 'quantity': item_quantity},
#     ]

#     # Calculate total price
#     total_price = sum(item['price'] * item['quantity'] for item in cart)

#     # Start the CXML response
#     cxml_response = f"""<PunchOutOrderMessage>
#     <BuyerCookie>123456</BuyerCookie>
#     <PunchOutOrderMessageHeader>
#         <Total>
#             <Money currency="INR">{total_price}</Money>
#         </Total>
#     </PunchOutOrderMessageHeader>"""

#     # Add each item in the cart
#     for item in cart:
#         cxml_response += f"""
#     <ItemIn quantity="{item['{item.quantity}']}">
#         <ItemID>
#             <SupplierPartID>{item['{item.name}']}</SupplierPartID>
#         </ItemID>
#         <ItemDetail>
#             <UnitPrice>
#                 <Money currency="INR">{item['{item.price}']}</Money>
#             </UnitPrice>
#         </ItemDetail>
#     </ItemIn>"""

#     # End the CXML response
#     cxml_response += "\n</PunchOutOrderMessage>"

#     return cxml_response

# # Route to get the CXML response
# @app.route('/generate_cxml', methods=['GET'])
# def get_cxml():
#     # Generate CXML
#     cxml_data = generate_cxml()
#     # Return as XML response
#     return Response(cxml_data, mimetype='application/xml')

# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Blueprint, render_template
from flask import Flask, Response, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session handling

punchout = Blueprint('punchout', __name__)

# Function to generate the CXML response based on the cart session data
def generate_cxml():
    # Retrieve the cart data from the session
    cart = session.get('cart1.cart', [])

    if not cart:
        return "<Error>Cart is empty</Error>"

    # Calculate the total price for the items in the cart
    total_price = sum(item['item.price'] * item['item.quantity'] for item in cart)

    # Start the cXML response
    cxml_response = f"""<PunchOutOrderMessage>
    <BuyerCookie>123456</BuyerCookie>
    <PunchOutOrderMessageHeader>
        <Total>
            <Money currency="INR">{total_price}</Money>
        </Total>
    </PunchOutOrderMessageHeader>"""

    # Add each item in the cart to the cXML
    for item in cart:
        cxml_response += f"""
    <ItemIn quantity="{item['item.quantity']}">
        <ItemID>
            <SupplierPartID>{item['item.name']}</SupplierPartID>
        </ItemID>
        <ItemDetail>
            <UnitPrice>
                <Money currency="INR">{item['item.price']}</Money>
            </UnitPrice>
        </ItemDetail>
    </ItemIn>"""

    # End the cXML response
    cxml_response += "\n</PunchOutOrderMessage>"

    return cxml_response

# Route to generate the CXML response
@punchout.route('/generate_cxml', methods=['GET'])
def get_cxml():
    # Generate the cXML data
    cxml_data = generate_cxml()
    # Return as XML response
    return Response(cxml_data, mimetype='application/xml')

if __name__ == '__main__':
    app.run(debug=True)

