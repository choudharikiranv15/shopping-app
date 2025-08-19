from core.db_helper import get_db_connection


def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'phone': row[2],
            'email': row[3],
            'address': row[4],
            'gender': row[5],
            'profile_pic_url': row[6],
            'profile_pic_file': row[7]
        }
    return None
