from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from core.db_helper import (
    get_all_categories,
    fetch_products_by_category,
    fetch_all_products,
    fetch_products_grouped_by_category
)


app = Flask(__name__)

# Function to fetch products from database


@app.route('/add-product', methods=['POST'])
def add_product():
    name = request.form.get('prodName')
    price = float(request.form.get('prodPrice', 0))
    category = request.form.get('prodCat')
    description = request.form.get('prodDesc')
    stock = int(request.form.get('prodStock', 0))

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
    categories = get_all_categories()
    products = fetch_products_grouped_by_category()
    return render_template("index.html", categories=categories, products=products)


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


if __name__ == '__main__':
    app.run(debug=True)
