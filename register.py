from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
import logging

# Import the centralized logging configuration
from logging_config import logging_config

# Create a logger specific to this module
logger = logging.getLogger("register1")

register1 = Blueprint('register1', __name__)

# Registration route
@register1.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm-password']

            logger.info("Registration attempted. Name: %s, Email: %s", name, email)

            # Password match validation
            if password != confirm_password:
                logger.warning("Passwords do not match for email: %s", email)
                flash('Passwords do not match!')
                return redirect(url_for('register1.register'))

            # Email validation
            if '@' not in email or '.' not in email:
                logger.warning("Invalid email format provided: %s", email)
                flash('Invalid email format!')
                return redirect(url_for('register1.register'))

            # Store the password as plain text (NOTE: Not secure; replace with hashing in production)
            plain_password = password

            # Database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Check if user already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                logger.warning("Registration failed: Email already exists. Email: %s", email)
                flash('Email already exists!')
                cursor.close()
                connection.close()
                return redirect(url_for('login1.login'))

            # Insert new user data into the database
            logger.info("Inserting new user: Name=%s, Email=%s", name, email)

            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                           (name, email, plain_password))
            connection.commit()
            logger.info("User registered successfully: Name=%s, Email=%s", name, email)

            cursor.close()
            connection.close()

            flash('Registration successful! You can now log in.')
            return redirect(url_for('login1.login'))

        except Exception as e:
            logger.error("Error during registration: %s", str(e), exc_info=True)
            flash('An unexpected error occurred. Please try again later.')
            return redirect(url_for('register1.register'))

    logger.info("Registration page accessed.")
    return render_template('register.html')
