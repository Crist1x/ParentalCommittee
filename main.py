import asyncio
import logging
import dotenv
import os
import sys

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import callbacks.kazna_callbacks, callbacks.user_callbacks
import utils.forms
from data.config import greeting_user_text, greeting_kazna_text, cansel_tranz
from keyboards.reply import greeting_user, greeting_kazna
from handlers import kazna_main, admin_main, user_main
from utils.forms import *
from data.functions import generate_schools_ikb, get_school_list, get_classes_list, get_letters_list


# Функция отправки фотографии перевода казначею
async def get_photo(message: Message, state: FSMContext):
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


async def confirmtranz(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.delete()
    await callback.message.answer("Вы подтвердили перевод!")

    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    user_data = cursor.execute(f"SELECT school, class, letter FROM users WHERE username='{user_id}'").fetchone()
    cursor.execute(f"INSERT INTO done (user_id, name, school, class, letter) VALUES ('{user_id}', '{callbacks.user_callbacks.name}', '{user_data[0]}', '{user_data[1]}', '{user_data[2]}');")

    connection.commit()
    cursor.close()

    await bot.send_message(user_id, "Казначей подтвердил перевод! Цель вычеркнута")


async def canseltranz(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.delete()
    await callback.message.answer("Вы отказали в подтверждении перевода!")
    await bot.send_message(user_id, cansel_tranz)


dotenv.load_dotenv(dotenv.find_dotenv())

# Инициализация бота и подключение роутеров
bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher()
dp.include_router(kazna_main.router)
dp.include_router(admin_main.router)
dp.include_router(user_main.router)

# Подключение Машины Состояния для получения карты казначея
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

# Подключение Машины Состояния для получения ника для удаления казначея
dp.message.register(utils.forms.del_treasurer, DelTreasurer.GET_NICKNAME)

# Регистрация колбеков для выбора необходимости цели
dp.callback_query.register(callbacks.kazna_callbacks.must_func, F.data == "must")
dp.callback_query.register(callbacks.kazna_callbacks.not_must_func, F.data == "not_must")

# Регистрация колбеков для прокрутки целей вперед-назад (kazna)
dp.callback_query.register(callbacks.kazna_callbacks.next_func, F.data == "next")
dp.callback_query.register(callbacks.kazna_callbacks.back_func, F.data == "back")

# Регистрация колбеков для прокрутки целей вперед-назад (user)
dp.callback_query.register(callbacks.user_callbacks.next_task, F.data == "forv")
dp.callback_query.register(callbacks.user_callbacks.back_task, F.data == "prev")
dp.callback_query.register(callbacks.user_callbacks.pay, F.data == "pay")

dp.callback_query.register(confirmtranz, F.data.startswith("confirmtranz_"))
dp.callback_query.register(canseltranz, F.data.startswith("canseltranz_"))

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
    if message.from_user.id not in kazna_list and message.from_user.id != os.getenv("ADMIN_USERNAME"):
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