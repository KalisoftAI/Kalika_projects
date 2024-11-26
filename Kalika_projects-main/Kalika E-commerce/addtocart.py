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

    cart = session['cart']

    # Check if the product is already in the cart
    existing_item = next((item for item in cart if item['itemcode'] == product_id), None)

    if existing_item:
        existing_item['quantity'] += 1
    else:
        cart.append({
            'itemcode': product_id,
            'name': item_name,
            'price': item_price,
            'quantity': 1
        })

    session['cart'] = cart
    session.modified = True

    # Inform the user of success
    flash(f"{item_name} added to cart!", "success")
    return redirect(url_for('cart1.cart'))