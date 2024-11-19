from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session

add_cart = Blueprint('add_cart', __name__)



@add_cart.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('product_name')
    item_price = request.form.get('product_price')

    if not item_name or not item_price:
        flash('Product name and price are required!', 'error')
        return redirect(url_for('home'))

    try:
        item_price = float(item_price)
    except ValueError:
        flash('Invalid price value!', 'error')
        return redirect(url_for('home'))

    if 'cart' not in session:
        session['cart'] = []

    # Check if the item is already in the cart
    for item in session['cart']:
        if item['name'] == item_name:
            item['quantity'] += 1
            break
    else:
        session['cart'].append({
            'name': item_name,
            'price': item_price,
            'quantity': 1
        })

    flash(f"{item_name} added to cart!", "success")
    return redirect(url_for('cart1.cart'))