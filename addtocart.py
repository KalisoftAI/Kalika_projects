from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db_connection
import logging

# Import the centralized logging configuration
from logging_config import logging_config

# Create a logger specific to this module
logger = logging.getLogger("add_cart")

add_cart = Blueprint('add_cart', __name__)



@add_cart.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('itemcode')
    item_name = request.form.get('product_name')
    item_price = request.form.get('product_price')
    image_url = request.form.get('image_url')  # Retrieve image URL

    # Log the incoming request data
    logger.info(f"Received request to add product to cart: itemcode={product_id}, name={item_name}, price={item_price}, image_url={image_url}")

    # Validate the input fields
    if not product_id or not item_name or not item_price or not image_url:
        flash('All product details are required!', 'error')
        logger.warning(f"Missing product details for item {item_name} (itemcode: {product_id})")
        return redirect(url_for('home'))

    try:
        item_price = float(item_price)
    except ValueError:
        flash('Invalid price value!', 'error')
        logger.error(f"Invalid price value for item {item_name} (itemcode: {product_id}): {item_price}")
        return redirect(url_for('home'))

    # Initialize the cart session if not already created
    if 'cart' not in session:
        session['cart'] = []
        logger.info("New cart session created")

    cart = session['cart']

    # Check if the product is already in the cart
    existing_item = next((item for item in cart if item['itemcode'] == product_id), None)

    if existing_item:
        existing_item['quantity'] += 1
        logger.info(f"Updated quantity of item {item_name} (itemcode: {product_id}) in cart to {existing_item['quantity']}")
    else:
        cart.append({
            'itemcode': product_id,
            'name': item_name,
            'price': item_price,
            'quantity': 1,
            'image_url': image_url
        })
        logger.info(f"Added new item {item_name} (itemcode: {product_id}) to cart")

    session['cart'] = cart
    session.modified = True

    flash(f"{item_name} added to cart!", "success")
    logger.info(f"Successfully added {item_name} (itemcode: {product_id}) to the cart")

    return redirect(url_for('cart1.cart'))