import sqlite3

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from utils.forms import AddCard, AddTask
import dotenv


dotenv.load_dotenv(dotenv.find_dotenv())
router = Router()


@router.message(F.text == "Привязать/Изменить карту")
async def add_card(message: Message, state: FSMContext):
    await message.answer("Введите номер карты (без лишних символов), который будет отображаться другим пользователям: ")
    await state.set_state(AddCard.GET_CARD)


@router.message(F.text == "Создать цель")
async def create_task(message: Message, state: FSMContext):
    await message.answer("Напишите название цели (кратко): ")
    await state.set_state(AddTask.GET_NAME)



