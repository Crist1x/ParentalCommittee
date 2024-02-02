from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

must_ikb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Да",
            callback_data="must"
        ), InlineKeyboardButton(
            text="Нет",
            callback_data="not_must"
        )
    ]
], resize_keyboard=True)