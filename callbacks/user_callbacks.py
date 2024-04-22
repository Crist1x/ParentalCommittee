from aiogram import Bot, types
from data.functions import get_classes_list, generate_classes_ikb


async def choose_class(callback: types.CallbackQuery):
    school = callback.data
    await callback.message.edit_text("Выберите класс, в котором учится ваш ребенок",
                                     reply_markup=generate_classes_ikb(school, get_classes_list(school)))
