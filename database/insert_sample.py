# database/insert_sample.py
import sqlite3


def insert_data():
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO products (name, price, category, description, stock) VALUES (?, ?, ?, ?, ?)",
                   ("Headphones", 1500, "Electronics", "Wireless Bluetooth", 20))
    cursor.execute("INSERT INTO products (name, price, category, description, stock) VALUES (?, ?, ?, ?, ?)",
                   ("Shoes", 2500, "Fashion", "Running Shoes", 15))

    conn.commit()
    conn.close()
    print("✅ Sample data inserted.")


if __name__ == '__main__':
    insert_data()
