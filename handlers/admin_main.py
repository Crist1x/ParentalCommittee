from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import dotenv

import keyboards.reply
from data.functions import admin_check
from utils.forms import AddTreasurer, DelTreasurer

dotenv.load_dotenv(dotenv.find_dotenv())
router = Router()


@router.message(Command("Add_Treasurer"))
async def add_treasurer(message: Message, state: FSMContext):
    if admin_check(message.from_user.id):
        await message.answer("Введите тг ник казначея: ",
                             reply_markup=keyboards.reply.back)
        await state.set_state(AddTreasurer.GET_NICKNAME)


@router.message(Command("Del_Treasurer"))
async def add_treasurer(message: Message, state: FSMContext):
    if admin_check(message.from_user.id):
        await message.answer("Введите тг ник казначея: ",
                             reply_markup=keyboards.reply.back)
        await state.set_state(DelTreasurer.GET_NICKNAME)
