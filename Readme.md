# 🍒 ShopEase – E-Commerce Web Application

ShopEase is a feature-rich, full-stack e-commerce web application built using **Flask**, **SQLite**, **HTML/CSS/JS**, and **TailwindCSS**. It supports both **customer** and **seller** functionalities, allowing users to browse, search, review, and purchase products, while sellers can manage their products and view order statistics.

---

## 🚀 Features

### 👤 Customer Side

* 📿 Register & Login (with OTP verification)
* 🔍 Browse, search, and view products
* 🛒 Add to Cart and adjust quantity
* ❤️ Add to Wishlist
* 💳 Buy Now & Checkout
* 💰 Payment Page (COD, Card, UPI, Netbanking)
* 📿 Order Confirmation Page
* 📦 Order History with product summary
* ✍️ Submit Reviews
* 🟡‍↗️ Edit Profile & Address

### 🧑‍🏫 Seller Side

* 📝 Seller Registration & Login
* ➕ Add Products with images
* 📋 View & Manage Products
* 📦 View Order Count Per Product (Dashboard)
* 📊 Product Analytics (basic)

---

## 🧱 Tech Stack

| Layer    | Technologies                                          |
| -------- | ----------------------------------------------------- |
| Frontend | HTML5, TailwindCSS, Vanilla JS, Animate.css, Lordicon |
| Backend  | Python (Flask)                                        |
| Database | SQLite                                                |
| Auth     | OTP Verification (Email-based)                        |
| UI/UX    | Fully responsive, Dark mode, Smooth animations        |

---

## 📁 Project Structure

```
project/
│
├── templates/                  # All HTML templates
│   ├── layout.html             # Base layout
│   ├── index.html              # Homepage
│   ├── product_detail.html     # Product info
│   ├── orders.html             # Order history page
│   ├── wishlist.html           # Wishlist page
│   ├── seller_dashboard.html   # Seller dashboard
│   └── ...
│
├── static/
│   ├── css/                    # Custom styles (if any)
│   └── images/                 # Product and placeholder images
│
├── database/
│   └── app.db                  # SQLite database
│
├── app.py                      # Main Flask application
├── core/                       # Modular Python helpers
│   ├── db_helper.py
│   ├── otp_helper.py
│   └── user_helper.py
│
└── README.md                   # Project documentation
```

---

## 🔑 Seller Login Access

* Seller login is **separate** from user login.
* Seller credentials are stored in a dedicated table.
* Route: `/seller_login`
* Dashboard: `/seller_dashboard`

---

## 🛠️ Setup Instructions

1. **Clone the repo:**

   ```bash
   git clone https://github.com/your-username/shopease.git
   cd shopease
   ```

2. **Create a virtual environment and activate it:**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python app.py
   ```

5. **Access in browser:**

   ```
   http://127.0.0.1:5000
   ```

---

## 🔐 Security Features

* OTP-based authentication
* Session handling for user & seller
* Form validation
* Wishlist access restricted to logged-in users

---

## 📸 Screenshots

* 🏠 Homepage
* 🛒 Product Detail
* ✅ Order Confirmation
* 📿 Seller Dashboard

---

## 🧠 Future Improvements

* 🔐 JWT-based API auth
* 📿 PDF Invoice generation
* 📦 Admin panel
* 📊 Sales analytics for sellers
* 📱 PWA support for mobile

---

## 🙌 Credits

Built with ❤️ by [Kiran Choudhari](https://www.linkedin.com/in/kiranchoudhari-1510m/)

---

##
