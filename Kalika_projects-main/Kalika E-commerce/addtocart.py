from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session

add_cart = Blueprint('add_cart', __name__)


@add_cart.route('/add_to_cart', methods=['POST'])  
def add_to_cart():
    item_name = request.form.get('product_name')
    item_price = request.form.get('product_price')

    session['cart'] = [{'item': item_name, 'quantity': item_price} for item_name, item_price in zip(item_name, item_price)] 
    # Check if product price and name are provided and valid
    if not item_name or item_price is None:
        flash('Product name and price are required!', 'error')
        return redirect(url_for('home'))  # Redirect to 'home' instead

    # Convert item_price to float after checking
    try:
        item_price = float(item_price)
    except ValueError:
        flash('Invalid price value!', 'error')
        return redirect(url_for('home'))

    # Initialize the cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []

    # session.pop('cart', None)
    # Add the item to the cart
    session['cart'].append({
        'name': item_name,
        'price': item_price
    })
    print("session1",session)

    # flash(f'Item {item_name} added to cart!', 'success')
    return redirect(url_for('cart1.cart'))
