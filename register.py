# register.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from db import get_db_connection
import logging

logger = logging.getLogger("register1")

register1 = Blueprint('register1', __name__)


@register1.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register1.register'))

        # Hash the password for security
        password_hash = generate_password_hash(password)

        connection = get_db_connection()
        if connection is None:
            flash('Database connection failed.', 'error')
            return redirect(url_for('register1.register'))

        try:
            with connection.cursor() as cursor:
                # Check if user already exists
                cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('An account with this email already exists.', 'error')
                    return redirect(url_for('register1.register'))

                # Insert new user
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (username, email, password_hash)
                )
                connection.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login1.login'))
        except Exception as e:
            logger.error(f"Error during registration: {e}", exc_info=True)
            flash('An error occurred during registration.', 'error')
            return redirect(url_for('register1.register'))

    return render_template('register.html')