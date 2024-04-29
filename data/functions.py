import sqlite3
import os
import dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

dotenv.load_dotenv(dotenv.find_dotenv())


# Проверка на казначея
def kazna_check(username):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    is_kaz = cursor.execute(f"SELECT username FROM kazna WHERE username = '{username}'").fetchone()
    cursor.close()
    return is_kaz


# Проверка на казначея
def admin_check(username):
    if os.getenv("ADMIN_USERNAME") == username:
        return True


# Генерация сообщения для списка целей
def generate_task(callback):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    kazna_data = cursor.execute(
        f"SELECT school, class, letter FROM kazna WHERE username = '{callback.from_user.username}'").fetchone()
    my_tasks = cursor.execute(f"SELECT name, description, price, date_finish, must FROM tasks WHERE "
                              f"school = '{kazna_data[0]}' AND class = '{kazna_data[1]}' AND letter = '{kazna_data[2]}'").fetchall()
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