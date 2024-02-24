import sqlite3

from aiogram import Bot, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold, hitalic

from data.functions import generate_task
from keyboards.inline import my_tasks_ikb
from keyboards.reply import greeting_admin, my_tasks_kb

task_indx = 0


# Если цель обязательна
async def must_func(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(must="Обязательно")
    all_data = await state.get_data()

    await task_confirm(all_data, state, bot, message)


# Если цель необязательна
async def not_must_func(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(must="Необязательно")
    all_data = await state.get_data()

    await task_confirm(all_data, state, bot, message)


async def next_func(callback: types.CallbackQuery):
    global task_indx

    my_tasks = generate_task(callback)

    if task_indx < len(my_tasks) - 1:
        task_indx += 1
        await callback.message.edit_text(f"""Название: {my_tasks[task_indx][0]}
Описание: {my_tasks[task_indx][1]}
Сумма (чел): {my_tasks[task_indx][2]}
Дедлайн: {my_tasks[task_indx][3]}   
Обязательность: {my_tasks[task_indx][4]}""", reply_markup=my_tasks_ikb)

    elif task_indx == len(my_tasks) - 1:
        await callback.answer("Это последняя цель")

    else:
        task_indx = 0
        await callback.message.edit_text(f"""Название: {my_tasks[task_indx][0]}
Описание: {my_tasks[task_indx][1]}
Сумма (чел): {my_tasks[task_indx][2]}
Дедлайн: {my_tasks[task_indx][3]}   
Обязательность: {my_tasks[task_indx][4]}""", reply_markup=my_tasks_ikb)


async def back_func(callback: types.CallbackQuery):
    global task_indx

    my_tasks = generate_task(callback)

    if task_indx > 0:
        task_indx -= 1
        await callback.message.edit_text(f"""Название: {my_tasks[task_indx][0]}
Описание: {my_tasks[task_indx][1]}
Сумма (чел): {my_tasks[task_indx][2]}
Дедлайн: {my_tasks[task_indx][3]}   
Обязательность: {my_tasks[task_indx][4]}""", reply_markup=my_tasks_ikb)

    elif task_indx == 0:
        await callback.answer("Это первая цель")

    else:
        task_indx = 0
        await callback.message.edit_text(f"""Название: {my_tasks[task_indx][0]}
Описание: {my_tasks[task_indx][1]}
Сумма (чел): {my_tasks[task_indx][2]}
Дедлайн: {my_tasks[task_indx][3]}   
Обязательность: {my_tasks[task_indx][4]}""", reply_markup=my_tasks_ikb)


# Итоговое создание цели
async def task_confirm(all_data, state, bot, message):
    total_text = f"""{hbold('ЦЕЛЬ СОЗДАНА 🎉')}

{hbold('Название:')} {all_data['name'].capitalize()}
{hbold('Описание:')} {all_data['desc'].capitalize()}
{hbold('Сумма (с человека):')} {all_data['price']} руб. 
{hbold('Дедлайн:')} до {all_data['date']}
{hbold('Необходимость:')} {all_data['must']}

{hitalic('Если вы хотите изменить цель, то можете сделать это в главном меню.')}"""

    try:
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        # Получаем данные о казначее
        comittee_info = cursor.execute(f"SELECT school, class, letter FROM admin WHERE username = '{message.from_user.username}'").fetchone()

        cursor.execute(f"INSERT INTO tasks (name, description, price, date_finish, must, school, class, letter) VALUES "
                       f"('{all_data['name'].capitalize()}', '{all_data['desc'].capitalize()}', {int(all_data['price'])}, "
                       f"'{all_data['date']}', '{all_data['must']}', '{comittee_info[0]}', '{comittee_info[1]}', '{comittee_info[2]}');")

        connection.commit()
        cursor.close()

        await state.clear()
        await bot.send_message(message.from_user.id,
                               total_text,
                               parse_mode=ParseMode.HTML,
                               reply_markup=greeting_admin)

    except ValueError:
        await state.clear()
        await bot.send_message(message.from_user.id,
                               "Не удалось создать цель. Возможно, при указании суммы были использованы не только "
                               "цифры. Попробуйте заново.",
                               reply_markup=greeting_admin)
