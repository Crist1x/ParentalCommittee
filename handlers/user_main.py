import sqlite3
import dotenv

from aiogram import Router, F
from aiogram.types import Message

from data.functions import user_reg_check, generate_schools_ikb, get_school_list
import keyboards.reply
from keyboards.inline import tasks_ikb

dotenv.load_dotenv(dotenv.find_dotenv())
router = Router()


@router.message(F.text == "Показать цели")
async def add_card(message: Message):
    if user_reg_check(message.from_user.username):
        await message.answer("Выберите цель, которую нужно оплатить из списка ниже. "
                             "(Для просмотра всех целей пользуйтесь стрелочками)")
        # Получение информации о всех целях конкретного класса
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        user_data = cursor.execute(
            f"SELECT school, class, letter FROM users WHERE username = '{message.from_user.username}'").fetchone()

        my_tasks = cursor.execute(f"SELECT name, description, price, date_finish, must FROM tasks WHERE "
                                  f"school = '{user_data[0]}' AND class = '{user_data[1]}' AND letter = '{user_data[2]}'").fetchall()

        try:
            await message.answer(f"""Название: {my_tasks[0][0]}
Описание: {my_tasks[0][1]}
Сумма (чел): {my_tasks[0][2]} ₽
Дедлайн: {my_tasks[0][3]}   
Обязательность: {my_tasks[0][4]}""", reply_markup=tasks_ikb)

            connection.commit()
            cursor.close()

        except IndexError:
            await message.answer("Активных целей на данный момент нет ✅")
    else:
        await message.answer("Сначала выберите класс обучения ребенка",
                             reply_markup=generate_schools_ikb(get_school_list()))
