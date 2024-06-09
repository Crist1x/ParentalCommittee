import sqlite3
import dotenv

from aiogram import Router, F
from aiogram.types import Message

from data.functions import user_reg_check, generate_schools_ikb, get_school_list
from keyboards.inline import tasks_ikb, user_history_ikb
from keyboards.reply import user_stats

dotenv.load_dotenv(dotenv.find_dotenv())
router = Router()


@router.message(F.text == "Показать цели")
async def add_card(message: Message):
    if user_reg_check(message.from_user.id):
        await message.answer("Выберите цель, которую нужно оплатить из списка ниже. "
                             "(Для просмотра всех целей пользуйтесь стрелочками)")
        # Получение информации о всех целях конкретного класса
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        user_data = cursor.execute(
            f"SELECT school, class, letter FROM users WHERE username = '{message.from_user.id}'").fetchone()

        done_tasks = cursor.execute(f"SELECT name FROM done WHERE user_id='{message.from_user.id}' AND "
                                    f"school = '{user_data[0]}' AND class = '{user_data[1]}' AND letter = '{user_data[2]}'").fetchall()
        my_tasks = cursor.execute(f"SELECT name, description, price, date_finish, must FROM tasks WHERE "
                                  f"school = '{user_data[0]}' AND class = '{user_data[1]}' AND letter = '{user_data[2]}'").fetchall()

        for done_task in done_tasks:
            for task in my_tasks:
                if done_task[0] == task[0]:
                    my_tasks.remove(task)

        try:
            await message.answer(f"""*Название:* {my_tasks[0][0]}
*Описание:* {my_tasks[0][1]}
*Сумма (чел):* {my_tasks[0][2]} ₽
*Дедлайн:* {my_tasks[0][3]}   
*Обязательность:* {my_tasks[0][4]}""", parse_mode="MARKDOWN", reply_markup=tasks_ikb)

            connection.commit()
            cursor.close()

        except IndexError:
            await message.answer("Активных целей на данный момент нет ✅")
    else:
        await message.answer("Сначала выберите класс обучения ребенка",
                             reply_markup=generate_schools_ikb(get_school_list()))


@router.message(F.text == "Открыть статистику")
async def stats(message: Message):
    if user_reg_check(message.from_user.id):
        await message.answer("Выберите интересующий вас раздел", reply_markup=user_stats)


@router.message(F.text == "История переводов 📜")
async def stats(message: Message):
    if user_reg_check(message.from_user.id):
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()

        done_info = cursor.execute(f"SELECT name, school, class, letter FROM done WHERE user_id = '{message.from_user.id}'").fetchall()
        tasks_info = []
        for item in done_info:
            data = cursor.execute(f"SELECT * FROM tasks WHERE name='{item[0]}' AND school='{item[1]}' AND class='{item[2]}' AND "
                                       f"letter='{item[3]}'").fetchone()
            if data:
                tasks_info.append(data)
            else:
                tasks_info.append([item[0], "информация была удалена казначеем", "информация была удалена казначеем", "информация была удалена казначеем", "информация была удалена казначеем"])

        connection.commit()
        cursor.close()

        if len(done_info) != 0:
            await message.answer(f"""✅ *ЦЕЛЬ ОПЛАЧЕНА* ✅
            
*Название:* {tasks_info[0][0]}
*Описание:* {tasks_info[0][1]}
*Сумма (чел):* {tasks_info[0][2]} ₽
*Дедлайн:* {tasks_info[0][3]}   
*Обязательность:* {tasks_info[0][4]}""", parse_mode="MARKDOWN", reply_markup=user_history_ikb)
        else:
            await message.answer("Вы не оплатили ни одной цели")
