from flask import Blueprint, render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db_connection

home = Blueprint('home', __name__)


# Index route
@home.route('/')
def home():
    user_name = None
    if 'user_id' in session:
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT name FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            if user:
                user_name = user[0]  # Get the name from the query result
        except Exception as e:
            print(f"Error retrieving user name: {e}")
        finally:
            cursor.close()
            connection.close()

    return render_template('index.html', user_name=user_name)  # Pass user_name to the template