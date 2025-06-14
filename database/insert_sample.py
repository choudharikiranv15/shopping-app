import sqlite3

conn = sqlite3.connect('database/app.db')
cursor = conn.cursor()

# Add columns to support both upload and URL
try:
    cursor.execute("ALTER TABLE profiles ADD COLUMN profile_pic_url TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE profiles ADD COLUMN profile_pic_file TEXT")
except:
    pass

conn.commit()
conn.close()

print("✅ profile_pic_url and profile_pic_file columns added.")
