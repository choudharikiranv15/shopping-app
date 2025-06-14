# database/init_db.py
import sqlite3


def init_db():
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            category TEXT,
            description TEXT,
            stock INTEGER
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized.")


if __name__ == '__main__':
    init_db()
