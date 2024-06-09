import sqlite3

from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hunderline

import keyboards.inline
from keyboards.reply import greeting_kazna, greeting_admin
from data.functions import change_task


class AddCard(StatesGroup):
    GET_CARD = State()
    GET_BANK = State()


async def get_card(message: Message, state: FSMContext):
    await state.update_data(card=message.text)
    data = await state.get_data()

    if data['card'] != "В меню":
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        cursor.execute(f"UPDATE kazna SET card_number = '{str(data['card'])}_{str(data['bank'])}' WHERE username = '{message.from_user.id}'")
        cursor.close()
        connection.commit()

        await message.answer(f"Все переводы теперь будут приходить на карту c номером {hbold(data['card'])} банка {hbold(data['bank'])}",
                             parse_mode=ParseMode.HTML, reply_markup=greeting_kazna)
    else:
        await message.answer("Вы вернулись в меню", reply_markup=greeting_kazna)

    await state.clear()


async def get_bank(message: Message, state: FSMContext):
    await state.update_data(bank=message.text)
    bank = await state.get_data()

    if bank['bank'] != "В меню":
        await message.answer("Введите номер карты (без лишних символов), который будет "
                             "отображаться другим пользователям:")
        await state.set_state(AddCard.GET_CARD)
    else:
        await message.answer("Вы вернулись в меню", reply_markup=greeting_kazna)
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


class GetTransferPhoto(StatesGroup):
    GET_PHOTO = State()
# Функция отправки фотографии перевода казначею находится в файле main


# Получение нового имени цели
class GetNewName(StatesGroup):
    NEW_NAME = State()


async def get_new_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await state.clear()

    change_task("name", data, message)

    await message.answer("Имя цели было успешно изменено!", reply_markup=greeting_kazna)


# Получение нового описания цели
class GetNewDesc(StatesGroup):
    NEW_DESC = State()


async def get_new_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text)
    data = await state.get_data()
    await state.clear()

    change_task("desc", data, message)

    await message.answer("Описание цели было успешно изменено!", reply_markup=greeting_kazna)


# Получение новой суммы цели
class GetNewSumm(StatesGroup):
    NEW_SUMM = State()


async def get_new_summ(message: Message, state: FSMContext):
    await state.update_data(summ=message.text)
    data = await state.get_data()
    await state.clear()

    change_task("summ", data, message)

    await message.answer("Сумма сбора средств на цель была успешна изменена!", reply_markup=greeting_kazna)


# Получение нового дедлайна цели
class GetNewDate(StatesGroup):
    NEW_DATE = State()


async def get_new_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    data = await state.get_data()
    await state.clear()

    change_task("date", data, message)

    await message.answer("Дедлайн цели был успешно изменен!", reply_markup=greeting_kazna)