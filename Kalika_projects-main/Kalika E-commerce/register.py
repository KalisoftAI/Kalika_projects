from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session
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
        print("name:", name, "email:", email )

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





