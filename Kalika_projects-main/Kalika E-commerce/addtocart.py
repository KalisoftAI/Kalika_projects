from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session

add_cart = Blueprint('add_cart', __name__)



@add_cart.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.form['item_id']
    item_name = request.form['product_name']
    item_price = float(request.form['product_price'])

    
    # Initialize the cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []

    # Add the item to the cart
    session['cart'].append({
        'id':item_id,
        'name': item_name,
        'price': item_price
    })
    print('add to cart',session['cart'])

    flash(f'Item {item_name} added to cart!', 'success')
    return redirect(url_for('view_cart'))

@add_cart.route('/view_cart')
def view_cart():
    cart_items = session.get('cart', [])
    total_amount = sum(item['price'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount)