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
            callback_data="back_usual"
        ), InlineKeyboardButton(
            text="➡️",
            callback_data="next_usual"
        )
    ]
], resize_keyboard=True)

my_tasks_ikb2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="⬅️",
            callback_data="back_stat"
        ), InlineKeyboardButton(
            text="➡️",
            callback_data="next_stat"
        )
    ]
], resize_keyboard=True)

tasks_ikb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="⬅️",
            callback_data="prev_no"
        ), InlineKeyboardButton(
            text="➡️",
            callback_data="forv_no"
        )
    ], [InlineKeyboardButton(
            text="Оплатить",
            callback_data="pay"
        )]
], resize_keyboard=True)

user_history_ikb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="⬅️",
            callback_data="prev_hist"
        ), InlineKeyboardButton(
            text="➡️",
            callback_data="forv_hist"
        )
    ]
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

new_must_ikb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Обязательна",
            callback_data="new_must"
        ), InlineKeyboardButton(
            text="Необязательна",
            callback_data="new_not_must"
        )
    ]
], resize_keyboard=True)
