import asyncio
import datetime
import logging
import os
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import callbacks.kazna_callbacks
import callbacks.user_callbacks
import data.functions
import utils.forms
from data.config import greeting_user_text, greeting_kazna_text, cansel_tranz
from data.functions import generate_schools_ikb, get_school_list, get_classes_list, get_letters_list
from handlers import kazna_main, admin_main, user_main
from keyboards.inline import my_tasks_ikb2
from keyboards.reply import greeting_user
from utils.forms import *


# Функция отправки фотографии перевода казначею
async def get_photo(message: Message, state: FSMContext):
    if message.text not in ("Показать цели", "В меню"):
        await state.update_data(photo=message.photo[-1].file_id, capture=message.text)
        photo = await state.get_data()
        await message.answer("Фотография успешно отправлена на верификацию казначею! Как только он подтвердит, цель будет вычеркнута из вашего списка")

        await state.clear()
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        user_data = cursor.execute(f"SELECT school, class, letter FROM users WHERE username='{message.from_user.id}'").fetchone()
        kazna_id = cursor.execute(f"SELECT username FROM kazna WHERE school='{user_data[0]}' AND class='{user_data[1]}' AND letter='{user_data[2]}'").fetchone()[0]

        if message.from_user.username is not None or message.from_user.username != '':
            text = f"@{message.from_user.username} перевел вам средства за цель с названием \"{callbacks.user_callbacks.name.rstrip()}\". Проверьте перевод в приложении вашего банка, и " \
                   f"если деньги были зачислены, то подтвердите перевод. В противном случае - отклоните"
        else:
            text = f"{message.from_user.last_name, message.from_user.first_name} перевел вам средства за цель с названием \"{callbacks.user_callbacks.name.rstrip()}\". Проверьте перевод в " \
                   f"приложении вашего банка, и если деньги были зачислены, то подтвердите перевод. В противном случае - " \
                   f"отклоните"

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подтвердить",
                    callback_data=f"confirmtranz_{message.from_user.id}"
                ),
                InlineKeyboardButton(
                    text="Отказать",
                    callback_data=f"canseltranz_{message.from_user.id}")
            ]
        ], resize_keyboard=True)

        await bot.send_photo(kazna_id, photo["photo"], caption=text, reply_markup=markup)

        connection.commit()
        cursor.close()
    else:
        await state.clear()
        if message.text == "В меню":
            await message.answer("Вы вернулись в меню", reply_markup=greeting_user)


async def confirmtranz(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.delete()
    await callback.message.answer("Вы подтвердили перевод!")

    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    user_data = cursor.execute(f"SELECT school, class, letter FROM users WHERE username='{user_id}'").fetchone()
    cursor.execute(f"INSERT INTO done (user_id, name, school, class, letter) VALUES ('{user_id}', '{callbacks.user_callbacks.name.strip()}', '{user_data[0]}', '{user_data[1]}', '{user_data[2]}');")

    connection.commit()
    cursor.close()

    await bot.send_message(user_id, "Казначей подтвердил перевод! Цель вычеркнута", reply_markup=greeting_user)


async def canseltranz(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.delete()
    await callback.message.answer("Вы отказали в подтверждении перевода!")
    await bot.send_message(user_id, cansel_tranz, reply_markup=greeting_user)

dotenv.load_dotenv(dotenv.find_dotenv())

# Инициализация бота и подключение роутеров
bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher()
dp.include_router(kazna_main.router)
dp.include_router(admin_main.router)
dp.include_router(user_main.router)

# Подключение Машины Состояния для получения карты казначея
dp.message.register(utils.forms.get_bank, AddCard.GET_BANK)
dp.message.register(utils.forms.get_card, AddCard.GET_CARD)

# Подключение Машины Состояния для получения фото перевода
dp.message.register(get_photo, GetTransferPhoto.GET_PHOTO)

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

dp.message.register(utils.forms.get_new_name, GetNewName.NEW_NAME)
dp.message.register(utils.forms.get_new_desc, GetNewDesc.NEW_DESC)
dp.message.register(utils.forms.get_new_summ, GetNewSumm.NEW_SUMM)
dp.message.register(utils.forms.get_new_date, GetNewDate.NEW_DATE)

# Подключение Машины Состояния для получения ника для удаления казначея
dp.message.register(utils.forms.del_treasurer, DelTreasurer.GET_NICKNAME)

# Регистрация колбеков для выбора необходимости цели
dp.callback_query.register(callbacks.kazna_callbacks.must_func, F.data == "must")
dp.callback_query.register(callbacks.kazna_callbacks.not_must_func, F.data == "not_must")

# Регистрация колбеков для прокрутки целей вперед-назад (kazna)
dp.callback_query.register(callbacks.kazna_callbacks.next_func, F.data.startswith("next_"))
dp.callback_query.register(callbacks.kazna_callbacks.back_func, F.data.startswith("back_"))

# Регистрация колбеков для прокрутки целей вперед-назад (user)
dp.callback_query.register(callbacks.user_callbacks.next_task, F.data.startswith("forv"))
dp.callback_query.register(callbacks.user_callbacks.back_task, F.data.startswith("prev"))
dp.callback_query.register(callbacks.user_callbacks.pay, F.data == "pay")

dp.callback_query.register(confirmtranz, F.data.startswith("confirmtranz_"))
dp.callback_query.register(canseltranz, F.data.startswith("canseltranz_"))

dp.callback_query.register(callbacks.kazna_callbacks.edit_name, F.data == "edit_name")
dp.callback_query.register(callbacks.kazna_callbacks.edit_desc, F.data == "edit_description")
dp.callback_query.register(callbacks.kazna_callbacks.edit_summ, F.data == "edit_price")
dp.callback_query.register(callbacks.kazna_callbacks.edit_date, F.data == "edit_date")
dp.callback_query.register(callbacks.kazna_callbacks.edit_must, F.data == "edit_must")
dp.callback_query.register(callbacks.kazna_callbacks.new_must, F.data == "new_must")
dp.callback_query.register(callbacks.kazna_callbacks.new_not_must, F.data == "new_not_must")

# Регистрация колбеков для выбора класса ученика
for school in get_school_list():
    dp.callback_query.register(callbacks.user_callbacks.choose_class, F.data == school)
    for class_ in get_classes_list(school):
        dp.callback_query.register(callbacks.user_callbacks.choose_letter, F.data == f"{school}_{class_}")
        for letter in get_letters_list(school, class_):
            dp.callback_query.register(callbacks.user_callbacks.class_confirmed, F.data == f"{school}_{class_}_{letter}")

dp.callback_query.register(callbacks.user_callbacks.back_to_schools, F.data == "backk_to_schools")
dp.callback_query.register(callbacks.user_callbacks.back_to_classes, F.data == "backk_to_classes")

# Хэндлер на команду /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    # Получение всех казначеев
    kazna_list = [i[0] for i in cursor.execute("SELECT username FROM kazna").fetchall()]

    # Если не от казначея
    if message.from_user.id not in kazna_list and message.from_user.id != int(os.getenv("ADMIN_USERNAME")):
        not_first_time = cursor.execute("SELECT username FROM users WHERE username=?",
                                        (message.from_user.id,)).fetchone()
        if not_first_time:
            await message.answer(greeting_user_text,
                                 reply_markup=greeting_user)
        else:
            await message.answer(greeting_user_text)
        # Если первый раз
        if not not_first_time:
            await message.answer("Выберите школу, в которой учится ваш ребенок", reply_markup=generate_schools_ikb(get_school_list()))

    # Если от казначея
    elif message.from_user.id in kazna_list:
        await message.answer(greeting_kazna_text,
                             reply_markup=greeting_kazna)
        is_card = cursor.execute(f"SELECT card_number FROM kazna WHERE username = '{message.from_user.id}'").fetchone()[0]
        if not is_card:
            await message.answer(f"Нажмите на кнопку \"{hbold('Привязать/Изменить карту')}\", чтобы создать первую цель для сбора.",
                                 parse_mode=ParseMode.HTML)
    else:
        await message.answer(
            f"Приветсвую, администратор!",
            reply_markup=greeting_admin)
    cursor.close()
    connection.commit()


@dp.message(F.text == "Список участников")
async def member_list(message: Message):
    if data.functions.kazna_check(message.from_user.id):
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        kd = cursor.execute(
            f"SELECT school, class, letter FROM kazna WHERE username = '{message.from_user.id}'").fetchone()
        # Получение всех участников
        member_list = [i[0] for i in cursor.execute(f"SELECT username FROM users WHERE school = '{kd[0]}' "
                                                    f"AND class = '{kd[1]}' AND letter = '{kd[2]}'").fetchall()]
        nicks = [j.username for j in [await bot.get_chat(int(i)) for i in member_list if type(i) == int]]
        text = f"👤 {hbold(f'Участники комитета')} 👤\n\n"

        for name in nicks:
            text += f"{nicks.index(name) + 1}. @{name}\n"

        await message.answer(text, parse_mode="HTML", reply_markup=greeting_kazna)


@dp.message(F.text == "История оплат")
async def stats(message: Message):
    if data.functions.kazna_check(message.from_user.id):
        import callbacks.kazna_callbacks
        callbacks.kazna_callbacks.stat_indx = 0

        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        kazna_data = cursor.execute(
            f"SELECT school, class, letter FROM kazna WHERE username = '{message.from_user.id}'").fetchone()

        my_tasks = cursor.execute(f"SELECT name, price, must FROM tasks WHERE "
                                  f"school = '{kazna_data[0]}' AND class = '{kazna_data[1]}' AND letter = '{kazna_data[2]}'").fetchall()
        text = f"""{hbold('Название:')} {my_tasks[0][0]}
{hbold('Сумма (чел):')} {my_tasks[0][1]}
{hbold('Обязательность:')} {my_tasks[0][2]}

{hbold('Список оплативших:')}\n"""

        user_id = [i[0] for i in cursor.execute(f"SELECT user_id FROM done WHERE name='{my_tasks[0][0]}' AND school = '{kazna_data[0]}' "
                               f"AND class = '{kazna_data[1]}' AND letter = '{kazna_data[2]}'").fetchall()]

        nicks = [j.username for j in [await bot.get_chat(int(i)) for i in user_id if type(i) == int]]

        for name in nicks:
            text += f"{nicks.index(name) + 1}. @{name}\n"

        # Генерирование сообщения с первой целью
        try:
            await message.answer(text, reply_markup=my_tasks_ikb2, parse_mode="HTML")

        except IndexError:
            await message.answer("Список целей пуст. Создайте новую в главном меню",
                                 reply_markup=greeting_kazna)

        connection.commit()
        cursor.close()
    else:
        await message.answer("Вы не указали реквизиты карты. Нажмите на кнопку *\"Привязать/Изменить карту\"*, и "
                             "следуйте инструкциям", parse_mode="MARKDOWN")


async def checking():
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    current_date = datetime.datetime.now()
    tomorrow = (current_date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')

    tasks_list = cursor.execute(f"SELECT name, school, class, letter FROM tasks WHERE date_finish='{tomorrow}'").fetchall()
    for obj in tasks_list:
        users_list = cursor.execute(f"SELECT username FROM users WHERE school = '{obj[1]}' "
                               f"AND class = '{obj[2]}' AND letter = '{obj[3]}'").fetchall()
        for user in users_list:
            await bot.send_message(chat_id=user[0], text=f"Не забудьте оплатить цель \"{obj[0]}\". "
                                                         f"Сегодня последний день оплаты")

    connection.commit()
    cursor.close()


# Запуск процесса поллинга новых апдейтов
async def main():
    try:
        scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        scheduler.add_job(checking, trigger='interval', hours=6)
        scheduler.start()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())