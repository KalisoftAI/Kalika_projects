from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
from flask import jsonify

login1 = Blueprint('login1', __name__)


# Login route
@login1.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password_hash')

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE (email = %s) AND password_hash = %s ",
                           (email, password))
            user = cursor.fetchone()

            if user and password(user[1], password):
                session['user_id'] = user[0]
                return jsonify({'success': True, 'message': 'Login successful!'})
            else:
                return jsonify({'success': False, 'message': 'Invalid email/mobile number or password!'})
        
        except Exception as e:
            print(f"Error during login: {e}")
            return jsonify({'success': False, 'message': 'Login failed! Please try again.'})

        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')