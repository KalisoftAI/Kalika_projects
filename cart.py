# cart.py (Completely Rewritten)
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection  # Import your database connection utility
import logging

logger = logging.getLogger("cart1")
cart1 = Blueprint('cart1', __name__, template_folder='templates')


@cart1.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Adds a product to the session cart."""
    try:
        product_code = request.form.get('code')  # Use the standardized 'code'
        product_name = request.form.get('name')
        product_price = request.form.get('price')
        image_url = request.form.get('image_url')

        if not all([product_code, product_name, product_price]):
            flash('Incomplete product details.', 'error')
            return redirect(request.referrer or url_for('home'))

        if 'cart' not in session:
            session['cart'] = []

        cart = session['cart']
        # Check if item already exists in cart
        existing_item = next((item for item in cart if item['code'] == product_code), None)

        if existing_item:
            existing_item['quantity'] += 1
        else:
            cart.append({
                'code': product_code,
                'name': product_name,
                'price': float(product_price),
                'quantity': 1,
                'image_url': image_url or url_for('static', filename='images/default.jpg')
            })

        session.modified = True  # Save the session changes
        flash(f'"{product_name}" was added to your cart!', 'success')

    except Exception as e:
        logger.error(f"Error in add_to_cart: {e}")
        flash('An error occurred while adding the item.', 'error')

    return redirect(request.referrer or url_for('home'))


@cart1.route('/cart')
def cart():
    """Displays the contents of the shopping cart."""
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@cart1.route('/update_cart/<product_code>', methods=['POST'])
def update_cart(product_code):
    """Updates the quantity of an item in the cart."""
    cart = session.get('cart', [])
    quantity = request.form.get('quantity', type=int)

    if quantity is not None and quantity > 0:
        for item in cart:
            if item['code'] == product_code:
                item['quantity'] = quantity
                break

    session.modified = True
    return redirect(url_for('cart1.cart'))


@cart1.route('/remove_from_cart/<product_code>', methods=['POST'])
def remove_from_cart(product_code):
    """Removes an item from the cart."""
    cart = session.get('cart', [])
    # Create a new cart list excluding the item to be removed
    session['cart'] = [item for item in cart if item['code'] != product_code]
    session.modified = True
    flash('Item removed from cart.', 'success')
    return redirect(url_for('cart1.cart'))


@cart1.route('/checkout')
def checkout():
    """Displays the checkout page with an order summary."""
    if 'user_id' not in session:
        flash('You must be logged in to proceed to checkout.', 'warning')
        return redirect(url_for('login1.login', next=url_for('cart1.checkout')))

    cart_items = session.get('cart', [])
    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('cart1.cart'))

    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)


@cart1.route('/process_order', methods=['POST'])
def process_order():
    """Processes the order and saves it to the database."""
    if 'user_id' not in session:
        return redirect(url_for('login1.login'))

    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('home'))

    shipping_address = request.form.get('address')
    if not shipping_address:
        flash("Shipping address is required.", "error")
        return redirect(url_for('cart1.checkout'))

    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    user_id = session['user_id']

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('cart1.checkout'))

    try:
        with conn.cursor() as cur:
            # 1. Insert into Orders table
            cur.execute(
                """
                INSERT INTO Orders (user_id, total_amount, shipping_address, status, payment_status)
                VALUES (%s, %s, %s, %s, %s) RETURNING order_id;
                """,
                (user_id, total_amount, shipping_address, 'Confirmed', 'Paid')
            )
            order_id = cur.fetchone()[0]

            # 2. Insert into order_items table for each item in the cart
            for item in cart:
                cur.execute(
                    """
                    INSERT INTO order_items (order_id, product_item_code, quantity, price_per_unit)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (order_id, item['code'], item['quantity'], item['price'])
                )

            conn.commit()

        # 3. Clear the cart from the session
        session.pop('cart', None)
        session.modified = True

        # Redirect to a new order confirmation page
        return redirect(url_for('cart1.order_confirmation', order_id=order_id))

    except Exception as e:
        logger.error(f"Error processing order: {e}")
        conn.rollback()
        flash("There was an error processing your order. Please try again.", "error")
        return redirect(url_for('cart1.checkout'))