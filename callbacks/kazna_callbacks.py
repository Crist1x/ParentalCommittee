import sqlite3

from aiogram import Bot, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold, hitalic

from data.functions import generate_task
from keyboards.inline import my_tasks_ikb, new_must_ikb, my_tasks_ikb2
from keyboards.reply import greeting_kazna
from utils.forms import GetNewName, GetNewDesc, GetNewSumm, GetNewDate

task_indx = 0
stat_indx = 0


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


async def next_func(callback: types.CallbackQuery, bot: Bot):
    global task_indx
    global stat_indx

    my_tasks = generate_task(callback, "no")

    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    if (task_indx < len(my_tasks) - 1 and callback.data.split("_")[1] == "usual") or (stat_indx < len(my_tasks) - 1 and callback.data.split("_")[1] != "usual"):
        if callback.data.split("_")[1] == "usual":
            task_indx += 1
            await callback.message.edit_text(f"""*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]}
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", reply_markup=my_tasks_ikb, parse_mode="MARKDOWN")
        else:
            stat_indx += 1
            text = f"""{hbold('Название:')} {my_tasks[stat_indx][0]}
{hbold('Сумма (чел):')} {my_tasks[stat_indx][2]}
{hbold('Обязательность:')} {my_tasks[stat_indx][4]}

{hbold('Список оплативших:')}\n"""

            kazna_data = cursor.execute(
                f"SELECT school, class, letter FROM kazna WHERE username = '{callback.from_user.id}'").fetchone()

            user_id = [i[0] for i in cursor.execute(
                f"SELECT user_id FROM done WHERE name='{my_tasks[stat_indx][0]}' AND school = '{kazna_data[0]}' "
                f"AND class = '{kazna_data[1]}' AND letter = '{kazna_data[2]}'").fetchall()]

            nicks = [j.username for j in [await bot.get_chat(int(i)) for i in user_id if type(i) == int]]

            for name in nicks:
                text += f"{nicks.index(name) + 1}. @{name}\n"

            await callback.message.edit_text(text, reply_markup=my_tasks_ikb2, parse_mode="HTML")

    elif (task_indx == len(my_tasks) - 1 and callback.data.split("_")[1] == "usual") or (stat_indx == len(my_tasks) - 1 and callback.data.split("_")[1] != "usual"):
        await callback.answer("Это последняя цель")

    else:
        if callback.data.split("_")[1] == "usual":
            task_indx = 0
            await callback.message.edit_text(f"""*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]}
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", reply_markup=my_tasks_ikb, parse_mode="MARKDOWN")
        else:
            stat_indx = 0
        text = f"""{hbold('Название:')} {my_tasks[stat_indx][0]}
{hbold('Сумма (чел):')} {my_tasks[stat_indx][2]}
{hbold('Обязательность:')} {my_tasks[stat_indx][4]}
    
{hbold('Список оплативших:')}\n"""

        kazna_data = cursor.execute(
            f"SELECT school, class, letter FROM kazna WHERE username = '{callback.from_user.id}'").fetchone()

        user_id = [i[0] for i in cursor.execute(
            f"SELECT user_id FROM done WHERE name='{my_tasks[stat_indx][0]}' AND school = '{kazna_data[0]}' "
            f"AND class = '{kazna_data[1]}' AND letter = '{kazna_data[2]}'").fetchall()]

        nicks = [j.username for j in [await bot.get_chat(int(i)) for i in user_id if type(i) == int]]

        for name in nicks:
            text += f"{nicks.index(name) + 1}. @{name}\n"

        await callback.message.edit_text(text, reply_markup=my_tasks_ikb2, parse_mode="HTML")

    connection.commit()
    cursor.close()


async def back_func(callback: types.CallbackQuery, bot: Bot):
    global task_indx
    global stat_indx

    my_tasks = generate_task(callback, "no")

    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    if (task_indx > 0 and callback.data.split("_")[1] == "usual") or (stat_indx > 0 and callback.data.split("_")[1] != "usual"):
        if callback.data.split("_")[1] == "usual":
            task_indx -= 1
            await callback.message.edit_text(f"""*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]}
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", reply_markup=my_tasks_ikb, parse_mode="MARKDOWN")
        else:
            stat_indx -= 1
            text = f"""{hbold('Название:')} {my_tasks[stat_indx][0]}
{hbold('Сумма (чел):')} {my_tasks[stat_indx][2]}
{hbold('Обязательность:')} {my_tasks[stat_indx][4]}

{hbold('Список оплативших:')}\n"""

            kazna_data = cursor.execute(
                f"SELECT school, class, letter FROM kazna WHERE username = '{callback.from_user.id}'").fetchone()

            user_id = [i[0] for i in cursor.execute(
                f"SELECT user_id FROM done WHERE name='{my_tasks[stat_indx][0]}' AND school = '{kazna_data[0]}' "
                f"AND class = '{kazna_data[1]}' AND letter = '{kazna_data[2]}'").fetchall()]

            nicks = [j.username for j in [await bot.get_chat(int(i)) for i in user_id if type(i) == int]]

            for name in nicks:
                text += f"{nicks.index(name) + 1}. @{name}\n"

            await callback.message.edit_text(text, reply_markup=my_tasks_ikb2, parse_mode="HTML")

    elif (task_indx == 0 and callback.data.split("_")[1] == "usual") or (stat_indx == 0 and callback.data.split("_")[1] != "usual"):
        await callback.answer("Это первая цель")

    else:
        if callback.data.split("_")[1] == "usual":
            task_indx = 0
            await callback.message.edit_text(f"""*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]}
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", reply_markup=my_tasks_ikb, parse_mode="MARKDOWN")
        else:
            stat_indx = 0
        text = f"""{hbold('Название:')} {my_tasks[stat_indx][0]}
{hbold('Сумма (чел):')} {my_tasks[stat_indx][2]}
{hbold('Обязательность:')} {my_tasks[stat_indx][4]}
    
{hbold('Список оплативших:')}\n"""

        kazna_data = cursor.execute(
            f"SELECT school, class, letter FROM kazna WHERE username = '{callback.from_user.id}'").fetchone()

        user_id = [i[0] for i in cursor.execute(
            f"SELECT user_id FROM done WHERE name='{my_tasks[stat_indx][0]}' AND school = '{kazna_data[0]}' "
            f"AND class = '{kazna_data[1]}' AND letter = '{kazna_data[2]}'").fetchall()]

        nicks = [j.username for j in [await bot.get_chat(int(i)) for i in user_id if type(i) == int]]

        for name in nicks:
            text += f"{nicks.index(name) + 1}. @{name}\n"

        await callback.message.edit_text(text, reply_markup=my_tasks_ikb2, parse_mode="HTML")
    connection.commit()
    cursor.close()


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
        comittee_info = cursor.execute(f"SELECT school, class, letter FROM kazna WHERE username = '{message.from_user.id}'").fetchone()

        cursor.execute(f"INSERT INTO tasks (name, description, price, date_finish, must, school, class, letter) VALUES "
                       f"('{all_data['name'].capitalize()}', '{all_data['desc'].capitalize()}', {int(all_data['price'])}, "
                       f"'{all_data['date']}', '{all_data['must']}', '{comittee_info[0]}', '{comittee_info[1]}', '{comittee_info[2]}');")

        connection.commit()
        cursor.close()

        await state.clear()
        await bot.send_message(message.from_user.id,
                               total_text,
                               parse_mode=ParseMode.HTML,
                               reply_markup=greeting_kazna)

    except ValueError:
        await state.clear()
        await bot.send_message(message.from_user.id,
                               "Не удалось создать цель. Возможно, при указании суммы были использованы не только "
                               "цифры. Попробуйте заново.",
                               reply_markup=greeting_kazna)


async def edit_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новое название цели: ")
    await state.set_state(GetNewName.NEW_NAME)


async def edit_desc(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новое описание цели: ")
    await state.set_state(GetNewDesc.NEW_DESC)


async def edit_summ(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новую сумму, которую нужно собрать с человека (только цифры):")
    await state.set_state(GetNewSumm.NEW_SUMM)


async def edit_date(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новую дату, до которой необходимо сдать деньги (формат 01.12.2023): ")
    await state.set_state(GetNewDate.NEW_DATE)


async def edit_must(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Выберите обязательна ли цель для каждого родителя", reply_markup=new_must_ikb)


async def new_must(callback: types.CallbackQuery):
    indx = task_indx
    task = generate_task(callback, "no")
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    kd = cursor.execute(f"SELECT school, class, letter FROM kazna WHERE username = '{callback.from_user.id}'").fetchone()
    cursor.execute(
        f"UPDATE tasks SET must='Обязательно' WHERE school = '{kd[0]}' AND class = '{kd[1]}' "
        f"AND letter = '{kd[2]}' AND name='{task[indx][0]}'")
    connection.commit()
    cursor.close()

    await callback.message.answer("Обязательность цели была успешна изменена!", reply_markup=greeting_kazna)


async def new_not_must(callback: types.CallbackQuery):
    indx = task_indx
    task = generate_task(callback, "no")
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    kd = cursor.execute(f"SELECT school, class, letter FROM kazna WHERE username = '{callback.from_user.id}'").fetchone()
    cursor.execute(
        f"UPDATE tasks SET must='Необязательно' WHERE school = '{kd[0]}' AND class = '{kd[1]}' "
        f"AND letter = '{kd[2]}' AND name='{task[indx][0]}'")
    connection.commit()
    cursor.close()

    await callback.message.answer("Обязательность цели была успешна изменена!", reply_markup=greeting_kazna)