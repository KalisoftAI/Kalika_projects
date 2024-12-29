from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

from db import get_db_connection
from psycopg2 import sql

cart1 = Blueprint('cart1', __name__)

@cart1.route('/cart', methods=['GET', 'POST'])
def cart():
    cart_items = session.get('cart', [])
    print("Debug: Cart items", cart_items)

    if request.method == 'GET':
        # Calculate total price for each item if it's missing
        for item in cart_items:
            if 'total_price' not in item:
                item['total_price'] = item['quantity'] * item['price']  # Calculate total price if missing
        total_amount = sum(item['total_price'] for item in cart_items)

        if request.headers.get('Accept') == 'application/json':
            return jsonify({"cart_items": cart_items, "total_amount": total_amount})
        else:
            return render_template('testcart.html', cart_items=cart_items, total_amount=total_amount)

    elif request.method == 'POST':
        data = request.get_json()
        itemcode = data.get('itemcode')
        action = data.get('action')

        if not itemcode or not action:
            return jsonify({"error": "Invalid request data"}), 400

        # Process the cart action
        for item in cart_items:
            if item['itemcode'] == itemcode:
                if action == 'increase':
                    item['quantity'] += 1
                elif action == 'decrease':
                    item['quantity'] -= 1
                    if item['quantity'] <= 0:
                        cart_items.remove(item)
                elif action == 'remove':
                    cart_items.remove(item)
                break

        # Update the total price for each item
        for item in cart_items:
            item['total_price'] = item['quantity'] * item['price']

        session['cart'] = cart_items
        session.modified = True  # Ensure session is updated
        total_amount = sum(item['total_price'] for item in cart_items)

        return jsonify({"cart_items": cart_items, "total_amount": total_amount})