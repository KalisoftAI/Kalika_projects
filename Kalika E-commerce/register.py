from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection

register1 = Blueprint('register1', __name__)

# Registration route
@register1.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register1.register'))

        # Validate email format (basic check)
        if '@' not in email or '.' not in email:
            flash('Invalid email format!')
            return redirect(url_for('register1.register'))

        # Do not hash the password, just store it as plain text
        plain_password = password  # Storing the password as is

        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email already exists!')
            cursor.close()
            connection.close()
            return redirect(url_for('login1.login'))

        # Insert new user data into the database
        print(f"Inserting user: Name={name}, Email={email}")

        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                       (name, email, plain_password))  # Use plain password here
        print("Data inserted successfully!")
        connection.commit()
        cursor.close()
        connection.close()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('login1.login'))

    return render_template('register.html')