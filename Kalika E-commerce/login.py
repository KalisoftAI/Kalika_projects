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

            # Fetch user data including name
            cursor.execute("SELECT user_id, password_hash, username FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                print(f"Login failed: No user found with email {email}")
                return jsonify({'success': False, 'message': 'Invalid email or password!'})

            user_id, stored_hash, username = user
            print(f"User found with email: {email}, Stored Hash: {stored_hash}")

            # Validate the password
            if check_password_hash(stored_hash, password):
                # Start session and store user information
                session['user_id'] = user_id  # Store the user ID in session
                session['user_email'] = email  # Store the user's email in session
                session['user_name'] = username  # Store the user's name in session
                session.permanent = True  # Make the session last longer if configured
                print(f"Login successful for user {user_id} - {email}")
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


@login1.route('/logout')
def logout():
    session.clear()  # Remove all session data
    return jsonify({'success': True, 'message': 'Logged out successfully!'})