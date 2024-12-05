from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db_connection

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

            # Fetch user data including name and plain password
            cursor.execute("SELECT user_id, password_hash, username FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                print(f"Login failed: No user found with email {email}")
                return jsonify({'success': False, 'message': 'Invalid email or password!'})

            user_id, stored_password, username = user
            print(f"User found with email: {email}, Stored Password: {stored_password}")

            # Validate the plain text password
            if stored_password == password:
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

    # Render login page for GET requests
    return render_template('login.html')


@login1.route('/get_user_info', methods=['GET'])
def get_user_info():
    print("userinfo", session)
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


@login1.route('/logout')
def logout():
    user_id = session.get('user_id')  # Fetch the current user's ID
    if user_id:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Save logout details to the database
            cursor.execute(
                "INSERT INTO session_logs (user_id, logout_time) VALUES (%s, NOW())",
                (user_id,)
            )
            connection.commit()

            # Optionally log this event
            print(f"Session data stored for user {user_id} at logout.")

        except Exception as e:
            print(f"Error saving session data: {e}")

        finally:
            # Close the connection
            cursor.close()
            connection.close()

    # Clear the session
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully!'})