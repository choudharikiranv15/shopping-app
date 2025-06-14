import sqlite3

DB_PATH = 'database/app.db'


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_categories():
    conn = get_db_connection()
    cursor = conn.execute("SELECT DISTINCT category FROM products")
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()
    return categories


def fetch_all_products():
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products


def fetch_products_by_category(category):
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM products WHERE category = ?", (category,)
    )
    products = cursor.fetchall()
    conn.close()
    return products


def fetch_products_grouped_by_category():
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()

    grouped = {}
    for row in rows:
        cat = row['category']
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(row)
    return grouped


def fetch_product_by_id(prod_id):
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM products WHERE id = ?", (prod_id,))
    product = cursor.fetchone()
    conn.close()
    return product
