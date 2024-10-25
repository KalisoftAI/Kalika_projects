from punchout import *
import secrets
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

# Set a random secret key for session management
app.secret_key = secrets.token_hex(16)  # Generates a random 32-character hex string

# Database connection parameters
db_host = "3.108.190.220" 
db_name = 'ecom_prod_catalog'
db_user = 'vikas'
db_password = 'kalika1667'

connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port='5432'
        )
cursor = connection.cursor()

# Connect to your PostgreSQL database
def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port='5432'
        )
        print("Database connected")
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")

get_db_connection()

# @app.route('/checkout', methods=['POST'])
# def checkout():
#     cart_items = request.json.get('cartItems', [])
#     user_id = request.json.get('userId')  # Assuming you have user ID from session or input

#     # Create a new order
#     conn = get_db_connection()
#     cur = conn.cursor()

#     cur.execute('INSERT INTO Orders (user_id, status) VALUES (%s, %s) RETURNING order_id',
#                 (user_id, 'Pending'))
#     order_id = cur.fetchone()[0]  # Get the newly created order ID

#     # Insert order items
#     for item in cart_items:
#         cur.execute('INSERT INTO OrderItems (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)',
#                     (order_id, item['product_id'], item['quantity'], item['price']))

#     print("Data inserted after checkout ")
#     conn.commit()
#     cur.close()
#     conn.close()

#     return jsonify({'message': 'Order placed successfully!', 'order_id': order_id}), 200

# Route for displaying products
@app.route('/products', methods=['GET', 'POST'])
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



# @app.route('/')
# def home():
#     return render_template('index.html')

# Index route
@app.route('/')
def home():
    user_name = None
    if 'user_id' in session:
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT name FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            if user:
                user_name = user[0]  # Get the name from the query result
        except Exception as e:
            print(f"Error retrieving user name: {e}")
        finally:
            cursor.close()
            connection.close()

    return render_template('index.html', user_name=user_name)  # Pass user_name to the template



# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))

        connection = get_db_connection()
        cursor = connection.cursor()
        # cursor.execute("SELECT * FROM users")

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email, ))
        existing_user = cursor.fetchone()

        # existing_user = cursor.fetchall()

        if existing_user:
            flash('Email already exists!')
            cursor.close()
            connection.close()
            return redirect(url_for('login'))
        
        print(f"Inserting user: Name={name}, Email={email}, Password={password}")

        cursor.execute(("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"),
                       (name, email, password))  # Store a hashed password in production!
        print("Data inserted successfully!")
        connection.commit()
        cursor.close()
        connection.close()

        # flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_mobile = request.form['email-mobile']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Validate user credentials
            cursor.execute("SELECT * FROM users WHERE (email = %s OR mobile = %s) AND password_hash = %s",
                           (email_or_mobile, email_or_mobile, password))  # Validate password properly
            user = cursor.fetchone()

            if user:
                session['user_id'] = user[0]  # Store user ID in session (first column of users table)
                flash('Login successful!')
                return redirect(url_for('/'))  # Redirect to index page after login
            else:
                flash('Invalid email/mobile number or password!')
        
        except Exception as e:
            print(f"Error during login: {e}")
            flash('Login failed! Please try again.')

        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')

# @app.route('/punchout', methods=['GET'])
# def punchout():
#     xml_response = create_punchout_request()
#
#     return Response(xml_response, mimetype='application/xml')



# Route for cart page
@app.route('/cart', methods=['GET', 'POST'])
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

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    
    item_name = request.form['product_name']
    item_price = float(request.form['product_price'])
    
    # Initialize the cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []

    # Add the item to the cart
    session['cart'].append({

        'name': item_name,
        'price': item_price
    })

    flash(f'Item {item_name} added to cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port='5432'
        )
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
        
    

    return redirect(url_for('cart'))

# Close the database connection on app teardown
@app.teardown_appcontext
def close_connection(exception):
    cursor.close()
    connection.close()

if __name__ == "__main__":
    app.run(debug=True)


# Route for Prouct page
