from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db_connection

add_cart = Blueprint('add_cart', __name__)



@add_cart.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Retrieve product details from the request
    product_id = request.form.get('itemcode')
    item_name = request.form.get('product_name')
    item_price = request.form.get('product_price')
    image_url = request.form.get('image_url')  # Retrieve image URL

    # Validate the input fields
    if not product_id or not item_name or not item_price or not image_url:
        flash('All product details are required!', 'error')
        return redirect(url_for('home'))

    try:
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
            'quantity': 1,
            'image_url': image_url
        })

    session['cart'] = cart
    session.modified = True

    flash(f"{item_name} added to cart!", "success")
    return redirect(url_for('cart1.cart'))