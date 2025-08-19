import os
import sqlite3

USE_POSTGRES = bool(os.getenv("DATABASE_URL"))

_pg = None
_DictCursor = None
if USE_POSTGRES:
    import psycopg2 as _pg
    from psycopg2.extras import DictCursor as _DictCursor

DB_PATH = 'database/app.db'


class PostgresCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=()):
        translated_query = query.replace('?', '%s')
        return self._cursor.execute(translated_query, params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def description(self):
        return self._cursor.description


class PostgresConnection:
    def __init__(self, dsn: str):
        # Neon requires SSL; psycopg2 honors sslmode in DSN if provided. Default to require.
        if 'sslmode=' not in dsn:
            if '?' in dsn:
                dsn = f"{dsn}&sslmode=require"
            else:
                dsn = f"{dsn}?sslmode=require"
        self._conn = _pg.connect(dsn, cursor_factory=_DictCursor)

    def cursor(self):
        return PostgresCursor(self._conn.cursor())

    # Provide sqlite-like convenience
    def execute(self, query, params=()):
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def commit(self):
        return self._conn.commit()

    def close(self):
        return self._conn.close()


def get_db_connection():
    if USE_POSTGRES:
        return PostgresConnection(os.environ['DATABASE_URL'])
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_categories():
    conn = get_db_connection()
    cursor = conn.execute("SELECT DISTINCT category FROM products")
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()
    return categories


def fetch_products_by_name(name_query):
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM products WHERE name LIKE ?", ('%' + name_query + '%',)
    )
    products = cursor.fetchall()
    conn.close()
    return products


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
    p = conn.execute("SELECT * FROM products WHERE id = ?",
                     (prod_id,)).fetchone()
    conn.close()
    return p
