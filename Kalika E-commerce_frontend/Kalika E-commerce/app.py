
from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='postgres',
        user='postgres',
        password='komal17'
    )
    return conn

# Route for displaying products
@app.route('/')
def products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT Product_Title as name, Product_Description as description, Price as price, image_url FROM kalika_catalog LIMIT 10;')
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('products.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
