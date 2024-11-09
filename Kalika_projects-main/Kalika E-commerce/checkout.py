from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
from datetime import datetime
from addtocart import add_cart


check = Blueprint('check', __name__)



@check.route('/checkout', methods=['POST'])
def checkout():
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Retrieve form data
    user_name = request.form.get('user_name')
    shipping_address = request.form.get('shipping_address')
    total_amount = float(request.form.get('total_amount', 0))
    payment_status = request.form.get('payment_status')
    order_date = datetime.now()
    cart_items = session.get('cart', [])

    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for('home'))

    try:
        # Find user_id from Users table using user_name
        cursor.execute("SELECT user_id FROM Users WHERE username = %s", (user_name,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            # Insert the order into the Orders table
            cursor.execute('''
                INSERT INTO Orders (user_id, order_date, total_amount, status, shipping_address, payment_status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING order_id
            ''', (user_id, order_date, total_amount, 'pending', shipping_address, payment_status, order_date, order_date))
            order_id = cursor.fetchone()[0]

            # Insert each cart item into the OrderItems table
            for item in cart_items:
                product_id = item['product_id']
                quantity = item['quantity']
                price = item['price']  # Assuming each item has a price field

                cursor.execute('''
                    INSERT INTO OrderItems (order_id, product_id, quantity, price, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (order_id, product_id, quantity, price, order_date, order_date))

            # Commit transaction
            connection.commit()

            # Flash success message and clear cart
            flash("Order placed successfully!", "success")
            session.pop('cart', None)  # Clears the entire cart

            return redirect(url_for('home'))
        else:
            flash("User not found. Please check your name.", "error")
            return redirect(url_for('cart1.cart'))  # Redirects to cart for retry

    except Exception as e:
        connection.rollback()
        flash(f"Error placing order: {e}", "error")
        return redirect(url_for('cart1.cart'))  # Redirects to cart for retry in case of error

    finally:
        cursor.close()
        connection.close()
