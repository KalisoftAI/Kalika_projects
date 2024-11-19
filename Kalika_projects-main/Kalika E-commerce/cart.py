from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

from db import get_db_connection
from psycopg2 import sql


cart1 = Blueprint('cart1', __name__)


# Route for cart page
@cart1.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'GET':
        # Handle GET request to fetch cart data
        cart_items = session.get('cart', [])
        if request.headers.get('Accept') == 'application/json':  # Check if the request expects JSON
            return jsonify({"cart_items": cart_items})  # Return JSON response
        else:
            return render_template('testcart.html', cart_items=cart_items)

    elif request.method == 'POST':
        # Handle POST request to update the cart
        cart_items = session.get('cart', [])
        data = request.get_json()
        item_id = data.get('id')
        action = data.get('action')

        # Find the item in the cart
        for item in cart_items:
            if item['id'] == item_id:
                if action == 'increase':
                    item['quantity'] += 1
                elif action == 'decrease':
                    item['quantity'] -= 1
                    if item['quantity'] <= 0:  # Remove item if quantity is 0
                        cart_items.remove(item)
                elif action == 'remove':
                    cart_items.remove(item)
                break

        # Update the session data
        session['cart'] = cart_items

        # Return updated cart items in the response
        return jsonify({"success": True, "cart_items": cart_items})