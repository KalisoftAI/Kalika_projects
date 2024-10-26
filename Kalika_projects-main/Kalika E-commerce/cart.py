from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session

from db import get_db_connection
from psycopg2 import sql

cart1 = Blueprint('cart1', __name__)

# Route for cart page
@cart1.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        user_name = request.form['user-name']
        
        # Connect to the database
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Insert user name into the database (assuming 'cart_users' table exists for cart-related actions)
                insert_query = sql.SQL("INSERT INTO cart_users (name) VALUES (%s)")
                cursor.execute(insert_query, (user_name,))
                conn.commit()
                cursor.close()
                conn.close()
                flash("Name saved successfully!", "success")
                return redirect(url_for('cart'))
            except Exception as e:
                flash(f"Error inserting data: {e}", "error")
                return redirect(url_for('cart'))
        else:
            flash("Database connection failed", "error")
            return redirect(url_for('cart'))
    
    return render_template('cart.html')