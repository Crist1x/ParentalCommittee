import sqlite3

from aiogram import Bot, types
from data.functions import get_classes_list, generate_classes_ikb, generate_letters_ikb, get_letters_list
from keyboards.reply import greeting_user


async def choose_class(callback: types.CallbackQuery):
    school = callback.data
    await callback.message.edit_text("Выберите класс, в котором учится ваш ребенок",
                                     reply_markup=generate_classes_ikb(school, get_classes_list(school)))


async def choose_letter(callback: types.CallbackQuery):
    school, class_ = callback.data.split("_")[0], callback.data.split("_")[1]
    await callback.message.edit_text("Выберите букву класса, в котором учится ваш ребенок",
                                     reply_markup=generate_letters_ikb(school, class_, get_letters_list(school, class_)))


async def class_confirmed(callback: types.CallbackQuery):
    callback_data = callback.data.split("_")
    school, class_, letter = callback_data[0], callback_data[1], callback_data[2]

    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    cursor.execute(f"""INSERT INTO users (username, school, class, letter) VALUES ('{callback.from_user.username}', '{school}',
                        '{class_}', '{letter}');""")
    cursor.close()
    connection.commit()
    await callback.message.answer(f"""Вы вступили в родительский комитет!
    
Школа: {school}
Класс: {class_}
Буква: {letter}""", reply_markup=greeting_user)