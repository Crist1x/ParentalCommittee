from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import dotenv

import keyboards.reply
from data.functions import admin_check
from utils.forms import AddTreasurer

dotenv.load_dotenv(dotenv.find_dotenv())
router = Router()


@router.message(Command("Add_Treasurer"))
async def add_treasurer(message: Message, state: FSMContext):
    if admin_check(message.from_user.username):
        await message.answer("Введите тг ник казначея: ",
                             reply_markup=keyboards.reply.back)
        await state.set_state(AddTreasurer.GET_NICKNAME)
