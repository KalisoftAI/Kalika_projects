from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
from datetime import datetime

check = Blueprint('check', __name__)

@check.route('/checkout', methods=['POST'])
def checkout():
    # connection = psycopg2.connect(
    #         host=db_host,
    #         database=db_name,
    #         user=db_user,
    #         password=db_password,
    #         port='5432'
    #     )
    connection = get_db_connection()
    cursor = connection.cursor()

    user_name = request.form['user_name']
    shipping_address = request.form['shipping_address']
    total_amount = float(request.form['total_amount'])
    payment_status = request.form['payment_status']
    order_date = datetime.now()

    cursor = connection.cursor()
    # Find user_id from Users table using user_name
    cursor.execute("SELECT user_id FROM Users WHERE username = %s", (user_name,))
    user = cursor.fetchone()

    

    try:
        if user:
            user_id = user[0]
            # Insert the order into the Orders table
            cursor.execute('''
                INSERT INTO Orders (user_id, order_date, total_amount, status, shipping_address, payment_status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, order_date, total_amount, 'pending', shipping_address, payment_status, order_date, order_date))
            connection.commit()
            flash("Order placed successfully!", "success")
            # Clear the cart after successful checkout
            session.pop('cart', None)  # Assuming 'cart' is the key used to store cart items
        else:
            flash("User not found. Please check your name.", "error")
    except Exception as e:
        connection.rollback()
        flash("Error placing order: " + str(e), "error")
        
    

    return redirect(url_for('cart1.cart'))