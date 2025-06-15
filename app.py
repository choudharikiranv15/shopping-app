from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from core.otp_helper import send_otp_email
from core.db_helper import (
    get_all_categories,
    fetch_products_by_category,
    fetch_all_products,
    fetch_products_grouped_by_category,
    fetch_product_by_id
)
from core.user_helper import get_user_by_id
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "7411971510$"
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def generate_and_send_otp(email):
    otp = str(random.randint(100000, 999999))
    session["otp"] = otp
    print(f"Generated OTP for {email}: {otp}")  # For development/debugging

    # Optional: Send OTP via email
    msg = MIMEText(f"Your OTP code is: {otp}")
    msg['Subject'] = "Your OTP Code"
    msg['From'] = "heybuddy20243@gmail.com"
    msg['To'] = email
    try:
        # Dummy: plug in real SMTP config here
        with smtplib.SMTP('smtp.mailtrap.io', 587) as server:
            server.starttls()
            server.login("your_username", "your_password")
            server.send_message(msg)
    except Exception as e:
        print("Email sending failed (expected on dev):", e)


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
            session['otp_verified'] = False  # Reset verification

            # Generate and store OTP in session
            otp = str(random.randint(100000, 999999))
            session['otp'] = otp

            # Send OTP via email (you already implemented this)
            from flask_mail import Mail, Message
            from core.mail_config import mail  # Assuming this is configured

            try:
                msg = Message(subject="Your OTP Code",
                              sender="your-email@gmail.com",
                              recipients=[row[3]])
                msg.body = f"Your OTP code is: {otp}"
                mail.send(msg)
                flash("OTP sent to your email", "info")
            except Exception as e:
                print(f"Failed to send OTP: {e}")
                flash("Error sending OTP. Try again later.", "danger")

            return redirect(url_for('verify_otp'))  # 👈 Redirect to OTP page

        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "pending_user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        entered_otp = request.form["otp"]
        if entered_otp == session.get("otp"):
            session["otp_verified"] = True
            session["user_id"] = session.pop("pending_user_id")
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


@app.route('/add-product', methods=['POST'])
def add_product():
    name = request.form.get('prodName')
    price = float(request.form.get('prodPrice', 0))
    category = request.form.get('prodCat')
    description = request.form.get('prodDesc')
    stock = int(request.form.get('prodStock', 0))
    image_url = request.form["image_url"]

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
    products = fetch_all_products()
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
    product_list = fetch_products()
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
        'phone': row[2],
        'email': row[3],
        'address': row[4],
        'gender': row[5],
        'profile_pic_url': row[6],
        'profile_pic_file': row[7]
    }

    return render_template("profile.html", user=user)


@app.route('/product/<int:prod_id>')
def product_detail(prod_id):
    product = fetch_product_by_id(prod_id)
    if not product:
        return "Product not found", 404
    return render_template("product_detail.html", product=product)


@app.route('/edit-profile', methods=['GET', 'POST'])
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
            'username': row[1],
            'phone': row[2],
            'email': row[3],
            'address': row[4],
            'gender': row[5],
            'profile_pic_url': row[6],
            'profile_pic_file': row[7]
        }

    return render_template('dashboard.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
