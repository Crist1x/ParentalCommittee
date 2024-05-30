from aiogram.filters.callback_data import CallbackData
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

my_tasks_ikb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="⬅️",
            callback_data="back"
        ), InlineKeyboardButton(
            text="➡️",
            callback_data="next"
        )
    ]
], resize_keyboard=True)

tasks_ikb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="⬅️",
            callback_data="prev"
        ), InlineKeyboardButton(
            text="➡️",
            callback_data="forv"
        )
    ], [InlineKeyboardButton(
            text="Оплатить",
            callback_data="pay"
        )]
], resize_keyboard=True)

edit_task_ikb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Название",
            callback_data="edit_name")
    ], [
        InlineKeyboardButton(
            text="Описание",
            callback_data="edit_description")
    ], [
        InlineKeyboardButton(
            text="Сумма",
            callback_data="edit_price")
    ], [
        InlineKeyboardButton(
            text="Дедлайн",
            callback_data="edit_date")
    ], [
        InlineKeyboardButton(
            text="Обязательность",
            callback_data="edit_must")
    ]
], resize_keyboard=True)