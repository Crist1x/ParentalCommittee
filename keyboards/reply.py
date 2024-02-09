from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

greeting_user = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Показать цели"), KeyboardButton(text="Открыть статистику")],
        [KeyboardButton(text="Помощь")]
    ], resize_keyboard=True)

greeting_admin = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Создать цель"), KeyboardButton(text="Мои цели")],
        [KeyboardButton(text="Привязать/Изменить карту")],
        [KeyboardButton(text="Помощь")]
    ], resize_keyboard=True)

back = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="В меню")]
    ], resize_keyboard=True)

