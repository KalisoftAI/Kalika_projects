from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session

add_cart = Blueprint('add_cart', __name__)



@add_cart.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Retrieve product details from the request
    product_id = request.form.get('itemcode')
    item_name = request.form.get('product_name')
    item_price = request.form.get('product_price')

    # Validate the input fields
    if not product_id or not item_name or not item_price:
        flash('Product ID, name, and price are required!', 'error')
        return redirect(url_for('home'))

    try:
        # Convert price to float
        item_price = float(item_price)
    except ValueError:
        flash('Invalid price value!', 'error')
        return redirect(url_for('home'))

    # Initialize the cart session if not already created
    if 'cart' not in session:
        session['cart'] = []

     # Debugging: Before Session add cart
    print("Current Cart:", session['cart'])

    # Ensure cart is a list
    cart = session['cart']

    # Check if the product is already in the cart
    product_found = False
    for item in cart:
        if item['itemcode'] == product_id:
            item['quantity'] += 1
            product_found = True
            break

    if not product_found:
        # Add new product if it's not in the cart
        cart.append({
            'itemcode': product_id,
            'name': item_name,
            'price': item_price,
            'quantity': 1
        })

    # Update session cart and mark it modified
    session['cart'] = cart
    session.modified = True

    # Debugging: Log the updated cart
    print("Updated Cart:", session['cart'])

    # Inform the user of success
    flash(f"{item_name} added to cart!", "success")
    return redirect(url_for('cart1.cart'))