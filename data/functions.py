import sqlite3
import os
import dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import callbacks

dotenv.load_dotenv(dotenv.find_dotenv())


# Проверка на казначея
def kazna_check(username):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    is_kaz = cursor.execute(f"SELECT username, card_number FROM kazna WHERE username = '{username}'").fetchone()
    cursor.close()
    if is_kaz:
        if is_kaz[1] is not None:
            return is_kaz


def user_reg_check(username):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    is_kaz = cursor.execute(f"SELECT school, class, letter FROM users WHERE username = '{username}'").fetchone()
    cursor.close()
    return is_kaz


# Проверка на казначея
def admin_check(username):
    if os.getenv("ADMIN_USERNAME") == username:
        return True


# Генерация сообщения для списка целей
def generate_task(callback, hist):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    is_kazna = kazna_check(callback.from_user.id)
    if is_kazna:
        data = cursor.execute(
            f"SELECT school, class, letter FROM kazna WHERE username = '{callback.from_user.id}'").fetchone()
        my_tasks = cursor.execute(f"SELECT name, description, price, date_finish, must FROM tasks WHERE "
                                  f"school = '{data[0]}' AND class = '{data[1]}' AND letter = '{data[2]}'").fetchall()
    else:
        if hist == "no":
            data = cursor.execute(
                f"SELECT school, class, letter FROM users WHERE username = '{callback.from_user.id}'").fetchone()
            done_tasks = cursor.execute(f"SELECT name FROM done WHERE user_id='{callback.from_user.id}' AND "
                                        f"school = '{data[0]}' AND class = '{data[1]}' AND letter = '{data[2]}'").fetchall()
            my_tasks = cursor.execute(f"SELECT name, description, price, date_finish, must FROM tasks WHERE "
                                      f"school = '{data[0]}' AND class = '{data[1]}' AND letter = '{data[2]}'").fetchall()
            for done_task in done_tasks:
                for task in my_tasks:
                    if done_task[0] == task[0]:
                        my_tasks.remove(task)
        else:
            done_info = cursor.execute(
                f"SELECT name, school, class, letter FROM done WHERE user_id = '{callback.from_user.id}'").fetchall()
            my_tasks = []

            for item in done_info:
                data = cursor.execute(
                    f"SELECT * FROM tasks WHERE name='{item[0]}' AND school='{item[1]}' AND class='{item[2]}' AND "
                    f"letter='{item[3]}'").fetchone()
                if data:
                    my_tasks.append(data)
                else:
                    my_tasks.append(
                        (item[0], "информация была удалена казначеем", "информация была удалена казначеем",
                         "информация была удалена казначеем", "информация была удалена казначеем"))

    connection.commit()
    cursor.close()

    return my_tasks


# Функция получения списка школ
def get_school_list():
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    schools = list(set([str(obj[0]) for obj in cursor.execute("SELECT school FROM kazna").fetchall()]))
    connection.commit()
    cursor.close()

    return schools


# функция получения готовой клавиатуры выбора школы
def generate_schools_ikb(schools):
    list1 = []
    if len(schools) % 2 == 0:
        for i in range(0, len(schools) // 2, 2):
            list1.append([
                InlineKeyboardButton(
                    text=schools[i],
                    callback_data=schools[i]),
                InlineKeyboardButton(
                    text=schools[i+1],
                    callback_data=schools[i+1])
            ])
        list1.append([
                InlineKeyboardButton(
                    text="Скрыть",
                    callback_data="hide_schools")]
        )
    else:
        for i in range(0, (len(schools) - 1) // 2, 2):
            list1.append([
                InlineKeyboardButton(
                    text=schools[i],
                    callback_data=schools[i]),
                InlineKeyboardButton(
                    text=schools[i+1],
                    callback_data=schools[i+1])
            ])
        list1.append([
            InlineKeyboardButton(
                text=schools[-1],
                callback_data=schools[-1]),
            InlineKeyboardButton(
                text="Скрыть",
                callback_data="hide_schools")
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=list1, resize_keyboard=True)


# Функция получения списка классов
def get_classes_list(school):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    classes = list(map(str, sorted([int(obj[0]) for obj in cursor.execute(f"SELECT class FROM kazna WHERE school='{school}'").fetchall()])))
    print(classes)
    connection.commit()
    cursor.close()
    return classes


# функция получения готовой клавиатуры выбора класса конкретной школы
def generate_classes_ikb(school, classes):
    list1 = []
    if len(classes) % 2 == 0:
        for i in range(0, len(classes) // 2, 2):
            list1.append([
                InlineKeyboardButton(
                    text=classes[i],
                    callback_data=f"{school}_{classes[i]}"),
                InlineKeyboardButton(
                    text=classes[i+1],
                    callback_data=f"{school}_{classes[i+1]}")
            ])
        list1.append([
                InlineKeyboardButton(
                    text="Назад",
                    callback_data="back_to_schools")]
        )
    else:
        for i in range(0, (len(classes) - 1) // 2, 2):
            list1.append([
                InlineKeyboardButton(
                    text=classes[i],
                    callback_data=f"{school}_{classes[i]}"),
                InlineKeyboardButton(
                    text=classes[i+1],
                    callback_data=f"{school}_{classes[i + 1]}")
            ])
        list1.append([
            InlineKeyboardButton(
                text=classes[-1],
                callback_data=f"{school}_{classes[-1]}"),
            InlineKeyboardButton(
                text="Назад",
                callback_data="back_to_schools")
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=list1, resize_keyboard=True)


def get_letters_list(school, class_):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    letters = list(map(str, sorted(
        [int(obj[0]) for obj in cursor.execute(f"SELECT letter FROM kazna WHERE school='{school}' AND class='{class_}'").fetchall()])))
    connection.commit()
    cursor.close()
    return letters


def generate_letters_ikb(school, class_, letters):
    list1 = []
    if len(letters) % 2 == 0:
        for i in range(0, len(letters) // 2, 2):
            list1.append([
                InlineKeyboardButton(
                    text=letters[i],
                    callback_data=f"{school}_{class_}_{letters[i]}"),
                InlineKeyboardButton(
                    text=letters[i+1],
                    callback_data=f"{school}_{class_}_{letters[i+1]}")
            ])
        list1.append([
                InlineKeyboardButton(
                    text="Назад",
                    callback_data="back_to_classes")]
        )
    else:
        for i in range(0, (len(letters) - 1) // 2, 2):
            list1.append([
                InlineKeyboardButton(
                    text=letters[i],
                    callback_data=f"{school}_{class_}_{letters[i]}"),
                InlineKeyboardButton(
                    text=letters[i+1],
                    callback_data=f"{school}_{class_}_{letters[i + 1]}")
            ])
        list1.append([
            InlineKeyboardButton(
                text=letters[-1],
                callback_data=f"{school}_{class_}_{letters[-1]}"),
            InlineKeyboardButton(
                text="Назад",
                callback_data="back_to_classes")
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=list1, resize_keyboard=True)


def change_task(param, data, message):
    indx = callbacks.kazna_callbacks.task_indx
    task = generate_task(message, "no")
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    kd = cursor.execute(f"SELECT school, class, letter FROM kazna WHERE username = '{message.from_user.id}'").fetchone()

    match param:
        case "name":
            cursor.execute(f"UPDATE tasks SET name='{data['name']}' WHERE school = '{kd[0]}' AND class = '{kd[1]}' "
                           f"AND letter = '{kd[2]}' AND name='{task[indx][0]}'")

        case "desc":
            cursor.execute(
                f"UPDATE tasks SET description='{data['desc']}' WHERE school = '{kd[0]}' AND class = '{kd[1]}' "
                f"AND letter = '{kd[2]}' AND name='{task[indx][0]}'")

        case "summ":
            cursor.execute(
                f"UPDATE tasks SET price='{data['summ']}' WHERE school = '{kd[0]}' AND class = '{kd[1]}' "
                f"AND letter = '{kd[2]}' AND name='{task[indx][0]}'")

        case "date":
            cursor.execute(
                f"UPDATE tasks SET date_finish='{data['date']}' WHERE school = '{kd[0]}' AND class = '{kd[1]}' "
                f"AND letter = '{kd[2]}' AND name='{task[indx][0]}'")

    connection.commit()
    cursor.close()