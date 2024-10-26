from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db_connection

login1 = Blueprint('login1', __name__)


# Login route
@login1.route('/login', methods=['GET', 'POST'])
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