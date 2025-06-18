from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import sqlite3
import os
import random
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from core.mail_config import mail, init_mail
from core.db_helper import (
    get_all_categories,
    fetch_products_by_category,
    fetch_all_products,
    fetch_products_grouped_by_category,
    fetch_product_by_id,
    fetch_products_by_name
)
from core.user_helper import get_user_by_id
from core.otp_helper import send_otp_email

app = Flask(__name__)
init_mail(app)
app.secret_key = "7411971510$"
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.context_processor
def inject_products():
    try:
        products = fetch_all_products()[:6]
    except:
        products = []
    return {'products': products}


@app.route('/')
def index():
    products_by_category = fetch_products_grouped_by_category()
    products = fetch_all_products() or []
    return render_template("index.html", products_by_category=products_by_category, products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]

        conn = sqlite3.connect('database/app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            flash("User already exists. Please log in.", "danger")
            return redirect("/login")

        hashed_pw = generate_password_hash(password)
        cursor.execute("INSERT INTO profiles (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hashed_pw))
        conn.commit()
        conn.close()

        flash("Registered successfully. Please log in.", "success")
        return redirect("/login")

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database/app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row and check_password_hash(row[8], password):
            session['user_id'] = row[0]
            session['user_email'] = row[3]
            session['otp_verified'] = False
            session['otp'] = str(random.randint(100000, 999999))

            try:
                send_otp_email(row[3], session['otp'])
                flash("OTP sent to your email", "info")
            except Exception as e:
                print(f"Failed to send OTP: {e}")
                flash("Error sending OTP. Try again later.", "danger")

            return redirect(url_for('verify_otp'))

        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        entered_otp = request.form["otp"]
        if entered_otp == session.get("otp"):
            session["otp_verified"] = True
            session.pop("otp", None)
            flash("OTP Verified!", "success")
            return redirect("/dashboard")
        else:
            flash("Incorrect OTP", "danger")
    return render_template("verify_otp.html")


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        conn = sqlite3.connect("database/app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            otp = str(random.randint(100000, 999999))
            session["reset_email"] = email
            session["otp"] = otp
            send_otp_email(email, otp)
            flash("OTP sent to your email", "info")
            return redirect(url_for("verify_otp_reset"))
        else:
            flash("Email not found", "danger")

    return render_template("forgot_password.html")


@app.route("/verify-otp-reset", methods=["GET", "POST"])
def verify_otp_reset():
    if request.method == "POST":
        entered_otp = request.form["otp"]
        if entered_otp == session.get("otp"):
            session["otp_verified_reset"] = True
            flash("OTP verified. Please reset your password.", "success")
            return redirect("/reset-password")
        else:
            flash("Incorrect OTP", "danger")
    return render_template("verify_otp_reset.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if not session.get("otp_verified_reset"):
        return redirect("/forgot-password")

    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect("/reset-password")

        email = session.get("reset_email")
        hashed_pw = generate_password_hash(new_password)

        conn = sqlite3.connect("database/app.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE profiles SET password = ? WHERE email = ?", (hashed_pw, email))
        conn.commit()
        conn.close()

        flash("Password reset successfully. Please login.", "success")
        session.clear()
        return redirect("/login")

    return render_template("reset_password.html")


@app.route('/products')
def products():
    product_list = fetch_products()
    products_by_category = defaultdict(list)
    for product in product_list:
        products_by_category[product['category']].append(product)
    return render_template("products.html", products_by_category=products_by_category)


@app.route('/products/<category>')
def show_category_products(category):
    products = fetch_products_by_category(category)
    return render_template("products.html", category=category, products=products)


@app.route('/product/<int:product_id>')
def view_product(product_id):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, name, description, price, image_url FROM products WHERE id = ?", (product_id,))
    row = c.fetchone()
    conn.close()

    if row:
        product = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': row[3],
            'image_url': row[4]
        }
        return render_template('product_detail.html', product=product)
    else:
        flash("Product not found.", "danger")
        return redirect(url_for('products'))


@app.route('/add-product', methods=['POST'])
def add_product():
    name = request.form.get('prodName')
    price = float(request.form.get('prodPrice', 0))
    category = request.form.get('prodCat')
    description = request.form.get('prodDesc')
    stock = int(request.form.get('prodStock', 0))
    image_url = request.form.get("image_url")

    if not name or not category:
        return "Missing required fields", 400

    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, category, description, stock, image_url) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, price, category, description, stock, image_url))
    conn.commit()
    conn.close()

    return redirect(url_for('products'))


def fetch_products():
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    products = []
    for row in rows:
        product = {
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'category': row[3],
            'description': row[4],
            'stock': row[5],
            'image_url': row[6] if len(row) > 6 else None
        }
        products.append(product)
    return products


@app.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("DELETE FROM wishlist WHERE user_id = ? AND product_id = ?",
              (user_id, product_id))
    conn.commit()
    conn.close()

    flash("Removed from wishlist.", "info")
    return redirect(url_for('wishlist'))


@app.route('/search')
def search():
    query = request.args.get('query', '')
    products = fetch_products_by_name(query)
    return render_template('search_results.html', query=query, products=products)


@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute('''
        SELECT cart.id as cart_id, products.*, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    ''', (user_id,))
    items = [dict(zip([col[0] for col in c.description], row))
             for row in c.fetchall()]
    conn.close()

    total_price = sum(item['price'] * item['quantity'] for item in items)

    return render_template('cart.html', items=items, total_price=total_price)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))  # fetch quantity from form

    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
              (user_id, product_id, quantity))
    conn.commit()
    conn.close()

    flash('Product added to cart!', 'success')
    return redirect(url_for('cart'))


@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    cart_id = int(request.form['cart_id'])
    quantity = int(request.form['quantity'])

    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("UPDATE cart SET quantity = ? WHERE id = ?", (quantity, cart_id))
    conn.commit()
    conn.close()

    flash('Cart updated!', 'success')
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:cart_id>')
def remove_from_cart(cart_id):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
    conn.commit()
    conn.close()
    flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()

    # Fetch product
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product_row = c.fetchone()

    if product_row is None:
        conn.close()
        flash("Product not found.", "danger")
        return redirect(url_for('index'))

    product = dict(zip([col[0] for col in c.description], product_row))
    category = product['category']

    # Related products
    c.execute("SELECT * FROM products WHERE category = ? AND id != ? LIMIT 6",
              (category, product_id))
    related_rows = c.fetchall()
    related_products = [
        dict(zip([col[0] for col in c.description], row)) for row in related_rows]

    # Fetch reviews
    c.execute('''
        SELECT r.rating, r.comment, r.created_at, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.product_id = ?
        ORDER BY r.created_at DESC
    ''', (product_id,))
    review_rows = c.fetchall()
    reviews = [dict(zip([col[0] for col in c.description], row))
               for row in review_rows]

    conn.close()

    return render_template(
        'product_detail.html',
        product=product,
        related_products=related_products,
        reviews=reviews
    )


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()

    if request.method == 'POST':
        import datetime
        import random

        address_id = request.form['address']
        payment_method = request.form['payment_method']

        # Fetch address details
        c.execute("""
            SELECT name, street, city, state, phone 
            FROM addresses 
            WHERE id = ? AND user_id = ?
        """, (address_id, user_id))
        address_data = c.fetchone()

        if not address_data:
            flash("Invalid address selected.", "danger")
            return redirect(url_for("checkout"))

        address = {
            "name": address_data[0],
            "street": address_data[1],
            "city": address_data[2],
            "state": address_data[3],
            "phone": address_data[4],
        }

        address_str = f"{address['name']}, {address['street']}, {address['city']}, {address['state']}, Phone: {address['phone']}"

        # Fetch cart items
        c.execute("""
            SELECT p.name, c.quantity, p.price 
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = ?
        """, (user_id,))
        cart_items = c.fetchall()

        if not cart_items:
            flash("Your cart is empty!", "warning")
            return redirect(url_for("cart"))

        items = []
        total_price = 0
        for name, qty, price in cart_items:
            items.append({
                "name": name,
                "quantity": qty,
                "price": price
            })
            total_price += qty * price

        # Create order ID and timestamp
        order_id = f"ORD{random.randint(1000,9999)}"
        order_date = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")

        # Save to orders table
        c.execute("""
            INSERT INTO orders (order_id, user_id, date, total, payment_method, shipping_address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            user_id,
            order_date,
            total_price,
            payment_method.upper(),
            address_str
        ))

        # Save to order_items table
        for item in items:
            c.execute("""
                INSERT INTO order_items (order_id, product_name, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (
                order_id,
                item["name"],
                item["quantity"],
                item["price"]
            ))

        # Clear the cart
        c.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        # Final order object for confirmation page
        order = {
            "id": order_id,
            "date": order_date,
            "payment_method": payment_method.upper(),
            "items": items,
            "total": total_price,
            "address": address
        }

        session['checkout_data'] = {
            'address_id': address_id,
            'payment_method': payment_method
        }

        # ✅ Important: Save order to session for confirmation page
        session['order'] = order

        if payment_method.lower() == 'cod':
            return redirect(url_for('order_confirmation'))

        return redirect(url_for('payment'))

    # GET request: Show addresses
    c.execute("SELECT * FROM addresses WHERE user_id = ?", (user_id,))
    addresses = c.fetchall()
    conn.close()
    return render_template("checkout.html", addresses=addresses)


# Add to Wishlist


@app.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login to add items to wishlist.", "warning")
        return redirect(url_for('login'))

    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("SELECT 1 FROM wishlist WHERE user_id = ? AND product_id = ?",
              (user_id, product_id))
    if c.fetchone():
        flash("Item already in wishlist.", "info")
    else:
        c.execute(
            "INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
        conn.commit()
        flash("Added to wishlist!", "success")
    conn.close()
    return redirect(request.referrer or url_for('products'))


# View Wishlist


@app.route('/wishlist')
def wishlist():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login to view your wishlist.", "warning")
        return redirect(url_for('login'))

    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("""
        SELECT p.id, p.name, p.price, p.image_url 
        FROM wishlist w 
        JOIN products p ON w.product_id = p.id 
        WHERE w.user_id = ?
    """, (user_id,))
    wishlist_items = c.fetchall()
    conn.close()

    return render_template('wishlist.html', wishlist_items=wishlist_items)


@app.route('/buy_now/<int:product_id>', methods=['POST'])
def buy_now(product_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login to continue.", "warning")
        return redirect(url_for('login'))

    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("SELECT name, price FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('products'))

    # Save to session and redirect to checkout
    session['buy_now'] = {
        'product_id': product_id,
        'name': product[0],
        'price': product[1],
        'quantity': 1
    }
    return redirect(url_for('checkout'))


@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY date DESC", (user_id,))
    orders = c.fetchall()

    order_list = []
    for order in orders:
        order_id = order['order_id']

        c.execute("""
            SELECT product_name, price, quantity
            FROM order_items
            WHERE order_id = ?
        """, (order_id,))
        items = c.fetchall()

        # ✅ plain text, no JSON decode
        shipping_address = order['shipping_address']

        order_dict = {
            "order_id": order['order_id'],
            "user_id": order['user_id'],
            "shipping_address": shipping_address,  # ✅ keep as string
            "payment_method": order['payment_method'],
            "total": order['total'],
            "order_date": order['order_date'],
            "date": order['date'],
            "items": [
                {"name": item['product_name'], "price": item['price'],
                 "quantity": item['quantity']}
                for item in items
            ]
        }
        order_list.append(order_dict)

    conn.close()
    return render_template("orders.html", orders=order_list)


def get_user_orders(user_id):
    conn = sqlite3.connect("D:/kiran/Pyspiders/Python/project/database/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    order_rows = cursor.fetchall()
    orders = []

    for row in order_rows:
        order_id = row["id"]

        # Fetch items
        cursor.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        item_rows = cursor.fetchall()
        items = [dict(item) for item in item_rows]

        # Fetch address
        cursor.execute(
            "SELECT * FROM addresses WHERE order_id = ?", (order_id,))
        address_row = cursor.fetchone()
        address = dict(address_row) if address_row else None

        order = {
            "order_id": order_id,
            "date": row["date"],
            "total": row["total"],
            "payment_method": row["payment_method"],
            "items": items,
            "address": address  # make sure this is a dict or None
        }

        orders.append(order)

    conn.close()
    return orders

# Submit a Review


@app.route('/submit_review/<int:product_id>', methods=['POST'])
def submit_review(product_id):
    if 'user_id' not in session:
        flash("Please log in to submit a review.", "warning")
        return redirect(url_for('login'))

    rating = int(request.form.get('rating', 0))
    comment = request.form.get('comment', '').strip()
    user_id = session['user_id']

    if not comment or rating == 0:
        flash("Please provide both rating and comment.", "danger")
        return redirect(url_for('product_detail', product_id=product_id))

    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("INSERT INTO reviews (user_id, product_id, rating, comment) VALUES (?, ?, ?, ?)",
              (user_id, product_id, rating, comment))
    conn.commit()
    conn.close()

    flash("Thank you for your review!", "success")
    return redirect(url_for('product_detail', product_id=product_id))


def get_reviews_for_product(product_id):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute('''
        SELECT r.rating, r.comment, r.created_at, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.product_id = ?
        ORDER BY r.created_at DESC
    ''', (product_id,))
    reviews = [dict(zip([col[0] for col in c.description], row))
               for row in c.fetchall()]
    conn.close()
    return reviews

# Address Routes


@app.route('/add_address', methods=['GET', 'POST'])
def add_address():
    if request.method == 'POST':
        user_id = session.get('user_id')
        name = request.form['name']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']
        phone = request.form['phone']

        conn = sqlite3.connect('database/app.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO addresses (user_id, name, street, city, state, pincode, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, street, city, state, pincode, phone))
        conn.commit()
        conn.close()
        flash('Address added successfully!', 'success')
        return redirect(url_for('checkout'))

    return render_template('add_address.html')


@app.route('/edit_address/<int:address_id>', methods=['GET', 'POST'])
def edit_address(address_id):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        city = request.form['city']
        pincode = request.form['pincode']
        phone = request.form['phone']

        c.execute('''
            UPDATE addresses 
            SET name=?, address=?, city=?, pincode=?, phone=? 
            WHERE id=?
        ''', (name, address, city, pincode, phone, address_id))
        conn.commit()
        conn.close()
        flash("Address updated successfully!", "success")
        return redirect(url_for('checkout'))

    # GET request
    c.execute("SELECT * FROM addresses WHERE id=?", (address_id,))
    address = c.fetchone()
    conn.close()

    if address:
        return render_template('edit_address.html', address=address)
    else:
        flash("Address not found.", "danger")
        return redirect(url_for('checkout'))


@app.route('/delete_address/<int:address_id>')
def delete_address(address_id):
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("DELETE FROM addresses WHERE id=?", (address_id,))
    conn.commit()
    conn.close()
    flash("Address deleted successfully.", "info")
    return redirect(url_for('checkout'))


@app.route('/order_confirmation')
def order_confirmation():
    # Safely get and remove the order from session
    order = session.pop('order', None)

    if not order:
        flash("Your order session has expired or no order found.", "warning")
        return redirect(url_for('products'))

    # Ensure address is structured (if passed as plain string earlier)
    if isinstance(order.get('address'), str):
        try:
            parts = order['address'].split(', ')
            order['address'] = {
                'name': parts[0],
                'street': parts[1],
                'city': parts[2],
                'state': parts[3],
                'phone': parts[4].replace("Phone: ", "")
            }
        except Exception:
            order['address'] = {
                'name': '-', 'street': '-', 'city': '-', 'state': '-', 'phone': '-'
            }

    return render_template('order_confirmation.html', order=order)


# 🔁 FINALIZE ORDER FUNCTION (returns dict, does not render)


def finalize_order(user_id, payment_method, address_str):
    import datetime
    import random
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()

    # Fetch cart items
    c.execute("""
        SELECT p.name, c.quantity, p.price 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
    """, (user_id,))
    cart_items = c.fetchall()

    if not cart_items:
        flash("Your cart is empty!", "warning")
        return None

    order_id = f"ORD{random.randint(1000, 9999)}"
    order_date = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
    total_price = sum(quantity * price for _, quantity, price in cart_items)

    # Insert into orders
    c.execute("""
        INSERT INTO orders (order_id, user_id, date, total, payment_method, shipping_address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (order_id, user_id, order_date, total_price, payment_method.upper(), address_str))

    # Insert into order_items
    for name, quantity, price in cart_items:
        c.execute("""
            INSERT INTO order_items (order_id, product_name, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, name, quantity, price))

    # Clear cart
    c.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    # Clear checkout session
    session.pop('checkout_data', None)

    return {
        "id": order_id,
        "date": order_date,
        "payment_method": payment_method.upper(),
        "items": [{"name": name, "quantity": quantity, "price": price} for name, quantity, price in cart_items],
        "total": total_price,
        "address": {
            "name": address_str.split(',')[0],
            "full": address_str
        }
    }


# Payment
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session or 'checkout_data' not in session:
        return redirect(url_for('checkout'))

    user_id = session['user_id']
    checkout_data = session['checkout_data']
    address_id = checkout_data['address_id']
    payment_method = checkout_data['payment_method']

    # Fetch address
    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("SELECT name, street, city, state, phone FROM addresses WHERE id = ? AND user_id = ?",
              (address_id, user_id))
    address_data = c.fetchone()
    conn.close()

    if not address_data:
        flash("Invalid address", "danger")
        return redirect(url_for('checkout'))

    address_str = f"{address_data[0]}, {address_data[1]}, {address_data[2]}, {address_data[3]}, Phone: {address_data[4]}"

    # Handle COD (finalize order immediately)
    if payment_method.lower() == 'cod':
        order = finalize_order(user_id, payment_method, address_str)
        if isinstance(order, dict):  # Order was successful
            session['order'] = order
            return redirect(url_for('order_confirmation'))
        else:
            return order  # This is likely a redirect due to empty cart

    # For Card, UPI etc., show the payment UI form
    return render_template("payment.html", payment_method=payment_method.lower())


@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session or 'checkout_data' not in session:
        return redirect(url_for('checkout'))

    user_id = session['user_id']
    checkout_data = session['checkout_data']
    address_id = checkout_data['address_id']
    payment_method = checkout_data['payment_method']

    conn = sqlite3.connect('database/app.db')
    c = conn.cursor()
    c.execute("SELECT name, street, city, state, phone FROM addresses WHERE id = ? AND user_id = ?",
              (address_id, user_id))
    address_data = c.fetchone()
    conn.close()

    if not address_data:
        flash("Invalid address.", "danger")
        return redirect(url_for("checkout"))

    address_str = f"{address_data[0]}, {address_data[1]}, {address_data[2]}, {address_data[3]}, Phone: {address_data[4]}"
    order = finalize_order(user_id, payment_method, address_str)

    if not order:
        return redirect(url_for("cart"))

    session['order'] = order
    return redirect(url_for('order_confirmation'))


@app.route('/profile')
def profile():
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return redirect(url_for('login'))

    user = {
        'username': row[1],
        'phone':    row[2],
        'email':    row[3],
        'address':  row[4],
        'gender':   row[5],
        'profile_pic_url':  row[6],
        'profile_pic_file': row[7]
    }

    return render_template("profile.html", user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_email' not in session or not session.get("otp_verified"):
        return redirect("/login")

    email = session.get('user_email')
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        address = request.form['address']
        gender = request.form.get('gender')
        profile_pic_url = request.form.get('profile_pic_url')

        profile_pic_file_path = None
        if 'profile_pic_file' in request.files:
            file = request.files['profile_pic_file']
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_path = os.path.join('static/uploads', filename)
                file.save(save_path)
                profile_pic_file_path = save_path

        cursor.execute("""
            UPDATE profiles
            SET username = ?, phone = ?, address = ?, gender = ?, profile_pic_url = ?, profile_pic_file = ?
            WHERE email = ?
        """, (username, phone, address, gender, profile_pic_url, profile_pic_file_path, email))
        conn.commit()
        conn.close()
        return redirect(url_for('profile'))

    cursor.execute("SELECT * FROM profiles WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return redirect(url_for('profile'))

    user = {
        'username': row[1],
        'phone': row[2],
        'email': row[3],
        'address': row[4],
        'gender': row[5],
        'profile_pic_url': row[6],
        'profile_pic_file': row[7]
    }
    return render_template("edit_profile.html", user=user)


@app.route('/edit-profile')
def legacy_edit_profile():
    return redirect(url_for('edit_profile'))


@app.route('/create-profile', methods=['POST'])
def create_profile():
    if 'user_email' not in session or not session.get("otp_verified"):
        return redirect("/login")

    username = request.form['username']
    phone = request.form['phone']
    email = session['user_email']
    address = request.form['address']
    gender = request.form.get('gender')
    profile_pic_url = request.form.get('profile_pic_url')

    profile_pic_file_path = None
    if 'profile_pic_file' in request.files:
        file = request.files['profile_pic_file']
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join('static/uploads', filename)
            file.save(save_path)
            profile_pic_file_path = save_path

    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE profiles SET username = ?, phone = ?, address = ?, gender = ?, profile_pic_url = ?, profile_pic_file = ?
        WHERE email = ?
    """, (username, phone, address, gender, profile_pic_url, profile_pic_file_path, email))
    conn.commit()
    conn.close()

    return redirect(url_for('profile'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('login'))

    email = session.get("user_email")
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    user = None
    if row:
        user = {
            'username':         row[1],
            'phone':            row[2],
            'email':            row[3],
            'address':          row[4],
            'gender':           row[5],
            'profile_pic_url':  row[6],
            'profile_pic_file': row[7]
        }

    return render_template("dashboard.html", user=user)


@app.route('/ajax/verify-otp', methods=['POST'])
def ajax_verify_otp():
    if "user_id" not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    data = request.get_json()
    entered_otp = data.get("otp")

    if entered_otp == session.get("otp"):
        session["otp_verified"] = True
        session.pop("otp", None)
        return jsonify({'success': True, 'message': 'OTP Verified'})
    else:
        return jsonify({'success': False, 'message': 'Incorrect OTP'}), 400


@app.route('/ajax/resend-otp', methods=['POST'])
def ajax_resend_otp():
    if "user_email" not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    otp = str(random.randint(100000, 999999))
    session["otp"] = otp

    try:
        send_otp_email(session['user_email'], otp)
        return jsonify({'success': True, 'message': 'OTP resent successfully'})
    except Exception as e:
        print(f"Failed to resend OTP: {e}")
        return jsonify({'success': False, 'message': 'Failed to resend OTP'}), 500


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
