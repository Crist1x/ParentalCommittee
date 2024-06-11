from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

greeting_user = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Показать цели")]
    , [KeyboardButton(text="Открыть статистику")]
    ], resize_keyboard=True)

greeting_admin = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="/Add_Treasurer")],
        [KeyboardButton(text="/Del_Treasurer")]
    ], resize_keyboard=True)

greeting_kazna = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Создать цель"), KeyboardButton(text="Мои цели")],
        [KeyboardButton(text="Привязать/Изменить карту"), KeyboardButton(text="Статистика")]
    ], resize_keyboard=True)

back = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="В меню")]
    ], resize_keyboard=True)

my_tasks_kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Отредактировать"), KeyboardButton(text="Удалить")],
        [KeyboardButton(text="В меню")]
    ], resize_keyboard=True)

user_stats = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="История переводов 📜")],
        [KeyboardButton(text="В меню")]
    ], resize_keyboard=True)


kazna_stats = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Список участников")],
        [KeyboardButton(text="История оплат")],
        [KeyboardButton(text="В меню")]
    ], resize_keyboard=True)