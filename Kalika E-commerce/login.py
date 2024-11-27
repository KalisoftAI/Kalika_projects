from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db_connection
from werkzeug.security import check_password_hash


login1 = Blueprint('login1', __name__)


# Login route
@login1.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Parse input data
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            # Validate input
            if not email or not password:
                return jsonify({'success': False, 'message': 'Email and password are required!'})

            # Connect to the database
            connection = get_db_connection()
            cursor = connection.cursor()

            # Fetch user data
            cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                print(f"Login failed: No user found with email {email}")
                return jsonify({'success': False, 'message': 'Invalid email or password!'})

            stored_hash = user[0]
            print(f"User found with email: {email}, Stored Hash: {stored_hash}")

            # Validate the password
            if check_password_hash(stored_hash, password):
                session['user_email'] = email
                print("Login successful")
                return jsonify({'success': True, 'message': 'Login successful!'})
            else:
                print("Login failed: Incorrect password")
                return jsonify({'success': False, 'message': 'Invalid email or password!'})

        except Exception as e:
            print(f"Error during login: {e}")
            return jsonify({'success': False, 'message': 'An unexpected error occurred. Please try again.'})

        finally:
            # Ensure the cursor and connection are closed
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Render login page for GET requests
    return render_template('login.html')