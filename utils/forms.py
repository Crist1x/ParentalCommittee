import sqlite3

from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

import keyboards.inline
from keyboards.reply import greeting_admin


class AddCard(StatesGroup):
    GET_CARD = State()


async def get_card(message: Message, state: FSMContext):
    await state.update_data(card=message.text)
    card_num = await state.get_data()
    if card_num['card'] != "В меню":
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        cursor.execute(f"UPDATE admin SET card_number = '{str(card_num['card'])}' WHERE username = '{message.from_user.username}'")
        cursor.close()
        connection.commit()

        await message.answer(f"Все переводы теперь будут приходить на карту c номером {hbold(card_num['card'])}",
                             parse_mode=ParseMode.HTML, reply_markup=greeting_admin)
        await state.clear()
    else:
        await message.answer("Вы вернулись в меню", reply_markup=greeting_admin)
        await state.clear()


class AddTask(StatesGroup):
    GET_NAME = State()
    GET_DESC = State()
    GET_PRICE = State()
    GET_DATE = State()
    GET_MUST = State()


async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Напишите описание для создаваемой цели: ")
    await state.set_state(AddTask.GET_DESC)


async def get_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer("Напишите сумму, которую нужно собрать с человека (только цифры): ")
    await state.set_state(AddTask.GET_PRICE)


async def get_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Напишите дату, до которой необходимо сдать деньги (формат 01.12.2023): ")
    await state.set_state(AddTask.GET_DATE)


async def get_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("Выберите обязательна ли цель для каждого человека: ",
                         reply_markup=keyboards.inline.must_ikb)


# Добавление казначея (для админки)
class AddTreasurer(StatesGroup):
    GET_NICKNAME = State()
    GET_SCHOOL = State()
    GET_CLASS = State()
    GET_LETTER = State()


async def get_nickname(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    data = await state.get_data()
    if data["nickname"] != "В меню":
        await message.answer("Напишите номер школы казначея:")
        await state.set_state(AddTreasurer.GET_SCHOOL)
    else:
        await message.answer("Вы вернулись в меню", reply_markup=greeting_admin)
        await state.clear()


async def get_school(message: Message, state: FSMContext):
    await state.update_data(school=message.text)
    data = await state.get_data()
    if data["school"] != "В меню":
        await message.answer("Напишите номер класса казначея (1-11):")
        await state.set_state(AddTreasurer.GET_CLASS)
    else:
        await message.answer("Вы вернулись в меню", reply_markup=greeting_admin)
        await state.clear()


async def get_class(message: Message, state: FSMContext):
    await state.update_data(clas=message.text)
    data = await state.get_data()
    if data["clas"] != "В меню":
        await message.answer("Напишите букву класса казначея:")
        await state.set_state(AddTreasurer.GET_LETTER)
    else:
        await message.answer("Вы вернулись в меню", reply_markup=greeting_admin)
        await state.clear()


async def get_letter(message: Message, state: FSMContext):
    await state.update_data(letter=message.text)
    data = await state.get_data()
    await state.clear()
    if data["letter"] != "В меню":
        try:
            connection = sqlite3.connect('db/database.db')
            cursor = connection.cursor()

            cursor.execute(f"INSERT INTO kazna (username, card_number, school, class, letter) VALUES "
                           f"('{data['nickname']}', '', '{data['school']}', '{data['clas']}', '{data['letter']}');")
            cursor.execute(f"DELETE FROM users WHERE username='{data['nickname']}'")

            connection.commit()
            cursor.close()

            await message.answer("Казначей успешно добавлен", reply_markup=greeting_admin)

        except Exception as e:
            print(e)
            await message.answer("Произошла ошибка", reply_markup=greeting_admin)
    else:
        await message.answer("Вы вернулись в меню", reply_markup=greeting_admin)
        await state.clear()


# Удаление казначея (для админки)
class DelTreasurer(StatesGroup):
    GET_NICKNAME = State()


async def del_treasurer(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    data = await state.get_data()
    await state.clear()

    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    if cursor.execute(f"SELECT * FROM kazna WHERE username = '{data['nickname']}'").fetchone():
        cursor.execute(f"DELETE FROM kazna WHERE username = '{data['nickname']}'")

        await message.answer("Казначей успешно удален", reply_markup=greeting_admin)

    else:
        await message.answer("Произошла ошибка. Скорее всего казначея с указанным ником не найдено!",
                             reply_markup=greeting_admin)
    connection.commit()
    cursor.close()
