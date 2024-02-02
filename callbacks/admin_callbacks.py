import sqlite3

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold, hitalic

from keyboards.reply import greeting_admin


async def must_func(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(must="Обязательно")
    all_data = await state.get_data()

    await task_write(all_data, state, bot, message)


async def not_must_func(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(must="Необязательно")
    all_data = await state.get_data()


    await task_write(all_data, state, bot, message)


async def task_write(all_data, state, bot, message):
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

        cursor.execute(f"INSERT INTO tasks (name, description, price, date_finish, must) VALUES "
                       f"('{all_data['name'].capitalize()}', '{all_data['desc'].capitalize()}', {int(all_data['price'])}, "
                       f"'{all_data['date']}', '{all_data['must']}');")

        connection.commit()
        cursor.close()

        await state.clear()
        await bot.send_message(message.from_user.id,
                               total_text,
                               parse_mode=ParseMode.HTML,
                               reply_markup=greeting_admin)
    except sqlite3.IntegrityError:
        await state.clear()
        await bot.send_message(message.from_user.id,
                               "Не удалось создать цель. Возможно, имя уже было использовано. Попробуйте заново.",
                               reply_markup=greeting_admin)
    except ValueError:
        await state.clear()
        await bot.send_message(message.from_user.id,
                               "Не удалось создать цель. Возможно, при указании суммы были использованы не только "
                               "цифры. Попробуйте заново.",
                               reply_markup=greeting_admin)
