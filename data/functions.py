import sqlite3


# Проверка на казначея
def kazna_chack(username):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    is_kaz = cursor.execute(f"SELECT username FROM admin WHERE username = '{username}'").fetchone()
    cursor.close()
    return is_kaz


# Генерация сообщения для списка целей
def generate_task(callback):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    kazna_data = cursor.execute(
        f"SELECT school, class, letter FROM admin WHERE username = '{callback.from_user.username}'").fetchone()
    my_tasks = cursor.execute(f"SELECT name, description, price, date_finish, must FROM tasks WHERE "
                              f"school = '{kazna_data[0]}' AND class = '{kazna_data[1]}' AND letter = '{kazna_data[2]}'").fetchall()
    connection.commit()
    cursor.close()

    return my_tasks
