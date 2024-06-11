import sqlite3

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import callbacks.kazna_callbacks
import data.functions
import keyboards.reply
from keyboards.inline import my_tasks_ikb
from utils.forms import AddCard, AddTask
from data.functions import kazna_check
import dotenv
import aioschedule, time

dotenv.load_dotenv(dotenv.find_dotenv())
router = Router()


# Хендлер привязки/изменения карты
@router.message(F.text == "Привязать/Изменить карту")
async def add_card(message: Message, state: FSMContext):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    # Получение всех казначеев
    kazna_list = [i[0] for i in cursor.execute("SELECT username FROM kazna").fetchall()]

    connection.commit()
    cursor.close()

    if message.from_user.id in kazna_list:
        await message.answer("Введите название банка, на который участники комитета будут переводить средства:",
                             reply_markup=keyboards.reply.back)
        await state.set_state(AddCard.GET_BANK)


# Хендлер создания цели
@router.message(F.text == "Создать цель")
async def create_task(message: Message, state: FSMContext):
    if kazna_check(message.from_user.id):
        await message.answer("Напишите название цели (кратко): ")
        await state.set_state(AddTask.GET_NAME)
    else:
        await message.answer("Вы не указали реквизиты карты. Нажмите на кнопку *\"Привязать/Изменить карту\"*, и "
                             "следуйте инструкциям", parse_mode="MARKDOWN")


# Хендлер мои цели
@router.message(F.text == "Мои цели")
async def my_tasks(message: Message):
    if kazna_check(message.from_user.id):
        import callbacks.kazna_callbacks
        callbacks.kazna_callbacks.task_indx = 0
        await message.answer("Здесь вы можете удалить или отредактировать ваши цели:",
                             reply_markup=keyboards.reply.my_tasks_kb)
        # Получение информации о всех целях конкретного казначея
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        kazna_data = cursor.execute(
            f"SELECT school, class, letter FROM kazna WHERE username = '{message.from_user.id}'").fetchone()
        my_tasks = cursor.execute(f"SELECT name, description, price, date_finish, must FROM tasks WHERE "
                                  f"school = '{kazna_data[0]}' AND class = '{kazna_data[1]}' AND letter = '{kazna_data[2]}'").fetchall()
        # Генерирование сообщения с первой целью
        try:
            await message.answer(f"""*Название:* {my_tasks[0][0]}
*Описание:* {my_tasks[0][1]}
*Сумма (чел):* {my_tasks[0][2]}
*Дедлайн:* {my_tasks[0][3]}   
*Обязательность:* {my_tasks[0][4]}""", reply_markup=my_tasks_ikb, parse_mode="MARKDOWN")

            connection.commit()
            cursor.close()
        except IndexError:
            await message.answer("Список целей пуст. Создайте новую в главном меню",
                                 reply_markup=keyboards.reply.greeting_kazna)
    else:
        await message.answer("Вы не указали реквизиты карты. Нажмите на кнопку *\"Привязать/Изменить карту\"*, и "
                             "следуйте инструкциям", parse_mode="MARKDOWN")


# Хендлер удалить цель
@router.message(F.text == "Удалить")
async def delete_task(message: Message):
    if kazna_check(message.from_user.id):
        indx = callbacks.kazna_callbacks.task_indx
        task = data.functions.generate_task(message, "no")
        connection = sqlite3.connect('db/database.db')
        cursor = connection.cursor()
        kd = cursor.execute(
            f"SELECT school, class, letter FROM kazna WHERE username = '{message.from_user.id}'").fetchone()
        cursor.execute(
            f"""DELETE FROM tasks WHERE name = '{task[indx][0]}' AND description = '{task[indx][1]}' AND price = '{task[indx][2]}'
                           AND date_finish = '{task[indx][3]}' AND must = '{task[indx][4]}' AND school = '{kd[0]}'
                           AND class = '{kd[1]}' AND letter = '{kd[2]}'""")
        connection.commit()
        cursor.close()
        await message.answer("Цель была успешно удалена", reply_markup=keyboards.reply.greeting_kazna)
    else:
        await message.answer("Вы не указали реквизиты карты. Нажмите на кнопку *\"Привязать/Изменить карту\"*, и "
                             "следуйте инструкциям", parse_mode="MARKDOWN")


# Хендлер возвращения в меню
@router.message(F.text == "В меню")
async def menu_back(message: Message):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()
    # Получение всех казначеев
    kazna_list = [i[0] for i in cursor.execute("SELECT username FROM kazna").fetchall()]

    connection.commit()
    cursor.close()

    if message.from_user.id in kazna_list:
        await message.answer("Вы вернулись в меню", reply_markup=keyboards.reply.greeting_kazna)
    elif data.functions.admin_check(message.from_user.id):
        await message.answer("Вы вернулись в меню", reply_markup=keyboards.reply.greeting_admin)
    else:
        await message.answer("Вы вернулись в меню", reply_markup=keyboards.reply.greeting_user)


# Хендлер редактирования цели
@router.message(F.text == "Отредактировать")
async def edit_task(message: Message):
    if kazna_check(message.from_user.id):
        await message.answer("Выберите параметр для редактирования:", reply_markup=keyboards.inline.edit_task_ikb)
    else:
        await message.answer("Вы не указали реквизиты карты. Нажмите на кнопку *\"Привязать/Изменить карту\"*, и "
                             "следуйте инструкциям", parse_mode="MARKDOWN")


@router.message(F.text == "Статистика")
async def stats(message: Message):
    if kazna_check(message.from_user.id):
        await message.answer("Выберите интересующий вас раздел", reply_markup=keyboards.reply.kazna_stats)
    else:
        await message.answer("Вы не указали реквизиты карты. Нажмите на кнопку *\"Привязать/Изменить карту\"*, и "
                             "следуйте инструкциям", parse_mode="MARKDOWN")


# Список участников находится в файле main