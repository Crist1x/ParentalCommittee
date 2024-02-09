import sqlite3


# Проверка на казначея
def kazna_chack(username):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    is_kaz = cursor.execute(f"SELECT username FROM admin WHERE username = '{username}'").fetchone()
    cursor.close()
    return is_kaz



