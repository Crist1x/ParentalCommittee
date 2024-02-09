from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import keyboards.reply
from utils.forms import AddCard, AddTask
from data.functions import kazna_chack
import dotenv


dotenv.load_dotenv(dotenv.find_dotenv())
router = Router()


# Хендлер привязки/изменения карты
@router.message(F.text == "Привязать/Изменить карту")
async def add_card(message: Message, state: FSMContext):
    if kazna_chack(message.from_user.username):

        await message.answer("Введите номер карты (без лишних символов), который будет отображаться другим пользователям: ",
                             reply_markup=keyboards.reply.back)
        await state.set_state(AddCard.GET_CARD)


# Хендлер создания цели
@router.message(F.text == "Создать цель")
async def create_task(message: Message, state: FSMContext):
    if kazna_chack(message.from_user.username):
        await message.answer("Напишите название цели (кратко): ")
        await state.set_state(AddTask.GET_NAME)


# Хендлер мои цели
@router.message(F.text == "Мои цели")
async def my_tasks(message: Message):
    if kazna_chack(message.from_user.username):
        await message.answer("Здесь вы можете удалить или отредактировать ваши цели",
                             reply_markup=...)



