import sqlite3

conn = sqlite3.connect('database/app.db')
cursor = conn.cursor()

cursor.execute("ALTER TABLE profiles ADD COLUMN password TEXT;")

conn.commit()
conn.close()
