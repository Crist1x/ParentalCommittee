import asyncio
import logging
import sqlite3
import dotenv
import os
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold

import callbacks.kazna_callbacks, callbacks.user_callbacks
import utils.forms
from data.config import greeting_user_text, greeting_kazna_text
from keyboards.reply import greeting_user, greeting_kazna, greeting_admin
from handlers import kazna_main, admin_main
from utils.forms import AddCard, AddTask, AddTreasurer, DelTreasurer
from data.functions import generate_schools_ikb, get_school_list, get_classes_list, get_letters_list


dotenv.load_dotenv(dotenv.find_dotenv())

# Инициализация бота и подключение роутеров
bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher()
dp.include_router(kazna_main.router)
dp.include_router(admin_main.router)

# Подключение Машины Состояния для получения карты казначея
dp.message.register(utils.forms.get_card, AddCard.GET_CARD)

# Подключение Машины Состояния для получения данных о цели
dp.message.register(utils.forms.get_name, AddTask.GET_NAME)
dp.message.register(utils.forms.get_desc, AddTask.GET_DESC)
dp.message.register(utils.forms.get_price, AddTask.GET_PRICE)
dp.message.register(utils.forms.get_date, AddTask.GET_DATE)

# Подключение Машины Состояния для получения данных о казначее
dp.message.register(utils.forms.get_nickname, AddTreasurer.GET_NICKNAME)
dp.message.register(utils.forms.get_school, AddTreasurer.GET_SCHOOL)
dp.message.register(utils.forms.get_class, AddTreasurer.GET_CLASS)
dp.message.register(utils.forms.get_letter, AddTreasurer.GET_LETTER)

# Подключение Машины Состояния для получения ника для удаления казначея
dp.message.register(utils.forms.del_treasurer, DelTreasurer.GET_NICKNAME)

# Регистрация колбеков для выбора необходимости цели
dp.callback_query.register(callbacks.kazna_callbacks.must_func, F.data == "must")
dp.callback_query.register(callbacks.kazna_callbacks.not_must_func, F.data == "not_must")

# Регистрация колбеков для прокрутки целей вперед-назад
dp.callback_query.register(callbacks.kazna_callbacks.next_func, F.data == "next")
dp.callback_query.register(callbacks.kazna_callbacks.back_func, F.data == "back")

# Регистрация колбеков для выбора класса ученика
for school in get_school_list():
    dp.callback_query.register(callbacks.user_callbacks.choose_class, F.data == school)
    for class_ in get_classes_list(school):
        dp.callback_query.register(callbacks.user_callbacks.choose_letter, F.data == f"{school}_{class_}")
        for letter in get_letters_list(school, class_):
            dp.callback_query.register(callbacks.user_callbacks.class_confirmed, F.data == f"{school}_{class_}_{letter}")

# Хэндлер на команду /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    # Получение всех казначеев
    kazna_list = [i[0] for i in cursor.execute("SELECT username FROM kazna").fetchall()]

    # Если не от казначея
    if message.from_user.username not in kazna_list and message.from_user.username != os.getenv("ADMIN_USERNAME"):
        not_first_time = cursor.execute("SELECT username FROM users WHERE username=?",
                                        (message.from_user.username,)).fetchone()
        if not_first_time:
            await message.answer(greeting_user_text,
                                 reply_markup=greeting_user)
        else:
            await message.answer(greeting_user_text)
        # Если первый раз
        if not not_first_time:
            await message.answer("Выберите школу, в которой учится ваш ребенок", reply_markup=generate_schools_ikb(get_school_list()))

    # Если от казначея
    elif message.from_user.username in kazna_list:
        await message.answer(greeting_kazna_text,
                             reply_markup=greeting_kazna)
        is_card = cursor.execute(f"SELECT card_number FROM admin WHERE username = '{message.from_user.username}'").fetchone()[0]
        if not is_card:
            await message.answer(f"Нажмите на кнопку \"{hbold('Привязать/Изменить карту')}\", чтобы создать первую цель для сбора.",
                                 parse_mode=ParseMode.HTML)
    else:
        await message.answer(
            f"Приветсвую, администратор!",
            reply_markup=greeting_admin)
    cursor.close()
    connection.commit()


# Запуск процесса поллинга новых апдейтов
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())