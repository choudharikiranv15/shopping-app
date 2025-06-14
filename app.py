from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from core.db_helper import (
    get_all_categories,
    fetch_products_by_category,
    fetch_all_products,
    fetch_products_grouped_by_category
)
from core.db_helper import fetch_product_by_id
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "7411971510$"  # Use a more secure key in production
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Function to fetch products from database


@app.route('/add-product', methods=['POST'])
def add_product():
    name = request.form.get('prodName')
    price = float(request.form.get('prodPrice', 0))
    category = request.form.get('prodCat')
    description = request.form.get('prodDesc')
    stock = int(request.form.get('prodStock', 0))
    image_url = request.form["image_url"]

    # Optional: validation
    if not name or not category:
        return "Missing required fields", 400

    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, category, description, stock) VALUES (?, ?, ?, ?, ?)",
                   (name, price, category, description, stock))
    conn.commit()
    conn.close()

    return redirect(url_for('products'))


def fetch_products():
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()

    # Convert DB rows to Product objects (optional, or use dicts)
    products = []
    for row in rows:
        product = {
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'category': row[3],
            'description': row[4],
            'stock': row[5]
        }
        products.append(product)
    return products


@app.route('/')
def index():
    products = fetch_all_products()  # You must have a function to fetch all products
    products_by_category = defaultdict(list)
    for p in products:
        products_by_category[p['category']].append(p)
    return render_template("index.html", products_by_category=products_by_category)


@app.route('/products/<category>')
def show_category_products(category):
    products = fetch_products_by_category(category)
    return render_template("products.html", category=category, products=products)


@app.route("/products")
def products():
    product_list = fetch_products()  # flat list
    products_by_category = defaultdict(list)
    for product in product_list:
        products_by_category[product['category']].append(product)
    return render_template("products.html", products_by_category=products_by_category)


@app.route('/cart')
def cart():
    return render_template("cart.html")


@app.route('/add-to-cart/<int:prod_id>')
def add_to_cart(prod_id):

    return redirect(url_for('cart'))


@app.route('/create-profile', methods=['POST'])
def create_profile():
    username = request.form['username']
    phone = request.form['phone']
    email = request.form['email']
    address = request.form['address']
    profile_pic_url = request.form.get('profile_pic_url', '').strip()

    # Handle file upload
    uploaded_file = request.files.get('profile_pic_file')
    profile_pic_file = None

    if uploaded_file and uploaded_file.filename:
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)
        profile_pic_file = file_path

    # Store in DB
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO profiles (username, phone, email, address, profile_pic_url, profile_pic_file)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, phone, email, address, profile_pic_url, profile_pic_file))
    conn.commit()
    conn.close()

    # Store in session for display
    session['user'] = {
        'username': username,
        'phone': phone,
        'email': email,
        'address': address,
        'profile_pic_url': profile_pic_url,
        'profile_pic_file': profile_pic_file
    }

    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        # Fetch the latest saved profile as fallback
        conn = sqlite3.connect('database/app.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, phone, email, address, gender, profile_pic FROM profiles ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            user = {
                'username': row[0],
                'phone': row[1],
                'email': row[2],
                'address': row[3],
                'gender': row[4],
                'profile_pic': row[5]
            }
            session['user'] = user
    return render_template("profile.html", user=user)


@app.route('/product/<int:prod_id>')
def product_detail(prod_id):
    product = fetch_product_by_id(prod_id)
    if not product:
        return "Product not found", 404
    return render_template("product_detail.html", product=product)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
