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

import callbacks.kazna_callbacks
import utils.forms
from data.config import greeting_user_text, greeting_admin_text
from keyboards.reply import greeting_user, greeting_admin
from handlers import kazna_main
from utils.forms import AddCard, AddTask


dotenv.load_dotenv(dotenv.find_dotenv())


bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher()
dp.include_router(kazna_main.router)

dp.message.register(utils.forms.get_card, AddCard.GET_CARD)
dp.message.register(utils.forms.get_name, AddTask.GET_NAME)
dp.message.register(utils.forms.get_desc, AddTask.GET_DESC)
dp.message.register(utils.forms.get_price, AddTask.GET_PRICE)
dp.message.register(utils.forms.get_date, AddTask.GET_DATE)

dp.callback_query.register(callbacks.kazna_callbacks.must_func, F.data == "must")
dp.callback_query.register(callbacks.kazna_callbacks.not_must_func, F.data == "not_must")


# Хэндлер на команду /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    # Получение всех казначеев
    admins_list = [i[0] for i in cursor.execute("SELECT username FROM admin").fetchall()]

    # Если не от казначея
    if message.from_user.username not in admins_list:
        not_first_time = cursor.execute("SELECT username FROM users WHERE username=?",
                                        (message.from_user.username,)).fetchone()
        # Если первый раз
        if not not_first_time:
            cursor.execute(f"""INSERT INTO users (username) VALUES ('{message.from_user.username}');""")

        await message.answer(greeting_user_text,
                             reply_markup=greeting_user)
    # Если от казначея
    elif message.from_user.username in admins_list:
        await message.answer(greeting_admin_text,
                             reply_markup=greeting_admin)
        is_card = cursor.execute(f"SELECT card_number FROM admin WHERE username = '{message.from_user.username}'").fetchone()[0]
        if not is_card:
            await message.answer(f"Нажмите на кнопку \"{hbold('Привязать/Изменить карту')}\", чтобы создать первую цель для сбора.",
                                 parse_mode=ParseMode.HTML)
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