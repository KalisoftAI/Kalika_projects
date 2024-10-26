from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session

from db import get_db_connection
from psycopg2 import sql

products1 = Blueprint('products1', __name__)



# Route for displaying products
@products1.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        # Handle "Add to Cart" functionality
        product_name = request.form.get('product_name')
        product_price = request.form.get('product_price')

        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                # Insert product into the cart table
                insert_query = sql.SQL("INSERT INTO cart (product_name, product_price) VALUES (%s, %s)")
                cur.execute(insert_query, (product_name, product_price))
                conn.commit()
                flash("Product added to cart successfully!", "success")
            except Exception as e:
                flash(f"Error adding product to cart: {e}", "error")
            finally:
                cur.close()
                conn.close()
        else:
            flash("Database connection failed", "error")

        return redirect(url_for('products'))

    # Existing logic to fetch product list from the database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT Product_Title as name, Product_Description as description, Price as price, image_url FROM kalika_catalog LIMIT 10;'
    )
    products = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('products.html', products=products)