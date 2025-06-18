# 🛒 ShopEase – E-Commerce Web App

**ShopEase** is a user-friendly, full-stack e-commerce web application built with **Flask (Python)** on the backend and a **responsive TailwindCSS** frontend. The platform allows users to register/login with OTP, browse products, add to cart, and manage their purchases with a smooth UI/UX experience.

---

## 🌟 Features

- 🔐 **User Authentication with OTP**
- 🗝️ **Forgot Password via OTP Email**
- 🛍️ **Product Browsing by Categories**
- ➕ **Add to Cart with Quantity Tracking**
- 🛒 **Cart Page with Dynamic Data**
- 💡 **Light & Dark Mode Toggle**
- 🎨 **Modern UI with Tailwind & Animate.css**
- 📧 **Email Integration via SMTP**
- ✅ **Responsive Design**

---

## 🧑‍💻 Tech Stack

### 🚀 Frontend
- **HTML, CSS, JavaScript**
- **TailwindCSS** for utility-first styling
- **Animate.css** for UI animations

### ⚙️ Backend
- **Python 3**
- **Flask** web framework
- **SQLite** lightweight relational DB

### 💌 Email + Extras
- **SMTP + smtplib** for OTP-based email verification
- **AJAX (Planned)** for dynamic OTP validation
- **Flask Sessions** for cart tracking

---

## 🛠️ Setup Instructions

Follow these steps to run the app locally:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/shopease.git
cd shopease

2. Create a Virtual Environment & Activate

python -m venv venv
venv\Scripts\activate   # Windows

3. Install Required Dependencies

pip install -r requirements.txt

4. Ensure the SQLite Database Exists

Make sure app.db is located at:

/database/app.db

If not, create it using a SQLite browser or helper script and include the following tables:

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    price REAL,
    category TEXT,
    image TEXT
);

CREATE TABLE cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER
);

5. Run the Flask App

python app.py

6. Visit in Browser

http://127.0.0.1:5000


---

📁 Project Structure

shopease/
│
├── app.py                      # Main Flask app
├── /core                       # Helper modules
│   ├── otp_helper.py
│   ├── db_helper.py
│   └── user_helper.py
│
├── /templates                  # HTML templates
│   ├── layout.html             # Shared layout
│   ├── index.html              # Homepage
│   ├── cart.html               # Cart page
│   ├── login.html              # User login
│   ├── register.html           # User signup
│   ├── forgot_password.html    # OTP reset
│   └── verify_otp.html
│
├── /static                     # Static files
│   ├── /css/
│   ├── /js/
│   └── /images/
│       ├── logo.png
│       ├── placeholder.png
│       └── empty-cart.svg
│
├── /database/
│   └── app.db                  # SQLite database
│
├── requirements.txt            # Required Python packages
└── README.md                   # This file


---

🧪 Features in Action

Users register/login using email OTP

Products are dynamically displayed on homepage

Cart persists across sessions (based on user ID)

Products added to the cart are stored in the DB

Empty cart displays an animated placeholder with a call-to-action button

🧡 Thank you for checking out ShopEase!
Made with ♥️ by Kiran Choudhari
