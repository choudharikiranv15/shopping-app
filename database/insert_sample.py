import sqlite3

conn = sqlite3.connect("database/app.db")
c = conn.cursor()

# Orders table
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    user_id INTEGER,
    date TEXT,
    total REAL,
    payment_method TEXT,
    address TEXT
)
""")

# Order Items table
c.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    product_name TEXT,
    quantity INTEGER,
    price REAL
)
""")

conn.commit()
conn.close()
print("Tables created successfully.")
