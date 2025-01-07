from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db_connection
import logging

# Import the centralized logging configuration
from logging_config import logging_config

# Create a logger specific to this module
logger = logging.getLogger("login1")

login1 = Blueprint('login1', __name__)

# Login route
@login1.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next', '/')  # Default to home if 'next' not provided
    logger.info("Login route accessed. Method: %s, Next URL: %s", request.method, next_url)

    if request.method == 'POST':
        try:
            # Parse input data
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                logger.warning("Login failed: Missing email or password.")
                return jsonify({'success': False, 'message': 'Email and password are required!'})

            # Connect to the database
            connection = get_db_connection()
            cursor = connection.cursor()

            # Fetch user data
            cursor.execute("SELECT user_id, password_hash, username FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                logger.warning("Login failed: No user found with email %s.", email)
                return jsonify({'success': False, 'message': 'Invalid email or password!'})

            user_id, stored_password, username = user
            logger.info("User found: %s, User ID: %d", email, user_id)

            # Validate the password (plain text comparison)
            if stored_password == password:
                session['user_id'] = user_id
                session['user_email'] = email
                session['user_name'] = username
                session.permanent = True
                logger.info("Login successful for user ID %d, Email: %s", user_id, email)

                return jsonify({
                    'success': True,
                    'message': 'Login successful!',
                    'redirect_url': next_url
                })
            else:
                logger.warning("Login failed: Incorrect password for email %s.", email)
                return jsonify({'success': False, 'message': 'Invalid email or password!'})

        except Exception as e:
            logger.error("Error during login: %s", str(e), exc_info=True)
            return jsonify({'success': False, 'message': 'An unexpected error occurred. Please try again.'})

    return render_template('login.html', next=next_url)

# Access User Info 
@login1.route('/get_user_info', methods=['GET'])
def get_user_info():
    logger.info("Accessing user info. Session data: %s", session)
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'user_name': session['user_name']
        })
    else:
        return jsonify({
            'success': False,
            'user_name': None
        })

# Logout Route
@login1.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO session_logs (user_id, logout_time) VALUES (%s, NOW())",
                (user_id,)
            )
            connection.commit()
            logger.info("Session data stored for user ID %d at logout.", user_id)

        except Exception as e:
            logger.error("Error saving session data for user ID %d: %s", user_id, str(e), exc_info=True)

        finally:
            cursor.close()
            connection.close()

    session.clear()
    logger.info("User ID %d logged out successfully.", user_id if user_id else "Unknown")
    return jsonify({'success': True, 'message': 'Logged out successfully!'})
