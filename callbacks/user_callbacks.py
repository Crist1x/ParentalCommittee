import sqlite3

from aiogram import types
from aiogram.fsm.context import FSMContext

from data.functions import get_classes_list, generate_classes_ikb, generate_letters_ikb, get_letters_list, \
    generate_task, generate_schools_ikb, get_school_list
from keyboards.inline import tasks_ikb, user_history_ikb
from keyboards.reply import greeting_user, back
from utils.forms import GetTransferPhoto

task_indx = 0
hist_indx = 0
name = ""
school_const = ""


async def choose_class(callback: types.CallbackQuery):
    global school_const
    school_const = callback.data
    await callback.message.edit_text("Выберите класс, в котором учится ваш ребенок",
                                     reply_markup=generate_classes_ikb(school_const, get_classes_list(school_const)))


async def choose_letter(callback: types.CallbackQuery):
    school, class_ = callback.data.split("_")[0], callback.data.split("_")[1]
    await callback.message.edit_text("Выберите букву класса, в котором учится ваш ребенок",
                                     reply_markup=generate_letters_ikb(school, class_, get_letters_list(school, class_)))


async def class_confirmed(callback: types.CallbackQuery):
    callback_data = callback.data.split("_")
    school, class_, letter = callback_data[0], callback_data[1], callback_data[2]

    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    cursor.execute(f"""INSERT INTO users (username, school, class, letter) VALUES ('{callback.from_user.id}', '{school}',
                        '{class_}', '{letter}');""")
    cursor.close()
    connection.commit()
    await callback.message.answer(f"""*Вы вступили в родительский комитет!*
    
*Школа:* {school}
*Класс:* {class_}
*Буква:* {letter}""", parse_mode="MARKDOWN", reply_markup=greeting_user)


async def next_task(callback: types.CallbackQuery):
    global task_indx

    my_tasks = generate_task(callback, callback.data.split("_")[1])

    print(my_tasks)

    if task_indx < len(my_tasks) - 1:
        task_indx += 1
        if callback.data.split("_")[1] == "hist":
            await callback.message.edit_text(f"""✅ *ЦЕЛЬ ОПЛАЧЕНА* ✅
    
*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]} ₽
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", parse_mode="MARKDOWN", reply_markup=user_history_ikb)
        else:
            await callback.message.edit_text(f"""*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]} ₽
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", parse_mode="MARKDOWN", reply_markup=tasks_ikb)

    elif task_indx == len(my_tasks) - 1:
        await callback.answer("Это последняя цель")

    else:
        task_indx = 0
        if callback.data.split("_")[1] == "hist":
            await callback.message.edit_text(f"""✅ *ЦЕЛЬ ОПЛАЧЕНА* ✅
    
*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]} ₽
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", parse_mode="MARKDOWN", reply_markup=user_history_ikb)
        else:
            await callback.message.edit_text(f"""*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]} ₽
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", parse_mode="MARKDOWN", reply_markup=tasks_ikb)


async def back_task(callback: types.CallbackQuery):
    global task_indx

    my_tasks = generate_task(callback, callback.data.split("_")[1])

    if task_indx > 0:
        task_indx -= 1
        if callback.data.split("_")[1] == "hist":
            await callback.message.edit_text(f"""✅ *ЦЕЛЬ ОПЛАЧЕНА* ✅
            
*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]} ₽
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", parse_mode="MARKDOWN", reply_markup=user_history_ikb)
        else:
            await callback.message.edit_text(f"""Название: {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]} ₽
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", parse_mode="MARKDOWN", reply_markup=tasks_ikb)

    elif task_indx == 0:
        await callback.answer("Это первая цель")

    else:
        task_indx = 0
        if callback.data.split("_")[1] == "hist":
            await callback.message.edit_text(f"""✅ *ЦЕЛЬ ОПЛАЧЕНА* ✅
    
*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]} ₽
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", parse_mode="MARKDOWN", reply_markup=user_history_ikb)
        else:
            await callback.message.edit_text(f"""*Название:* {my_tasks[task_indx][0]}
*Описание:* {my_tasks[task_indx][1]}
*Сумма (чел):* {my_tasks[task_indx][2]} ₽
*Дедлайн:* {my_tasks[task_indx][3]}   
*Обязательность:* {my_tasks[task_indx][4]}""", parse_mode="MARKDOWN", reply_markup=tasks_ikb)


async def pay(callback: types.CallbackQuery, state: FSMContext):
    global name

    message_data = callback.message.text

    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    school_info = cursor.execute(f"SELECT school, class, letter FROM users WHERE username = {callback.from_user.id}").fetchone()
    kazna_card = cursor.execute(f"SELECT card_number FROM kazna WHERE school = '{school_info[0]}' AND class = '{school_info[1]}' AND letter = '{school_info[2]}'").fetchone()[0]

    cursor.close()
    connection.commit()

    await callback.message.answer(f"*Цель:* {message_data.split('Название: ')[1].split('Описание:')[0]}"
                                  f"*Реквизиты для перевода:* `{kazna_card.split('_')[0]}`  {kazna_card.split('_')[1]}(Нажмите для копирования)\n"
                                  f"*К оплате:* {message_data.split('Сумма (чел): ')[1].split(' ₽')[0]} ₽"
                                  f"\n\nПосле оплаты пришлите фотографию чека. "
                                  f"Следующим шагом можно будет оставить комментарий "
                                  f"(например, если перевод был выполнен от 3-его лица.)", parse_mode="MARKDOWN",
                                  reply_markup=back)

    name = message_data.split('Название: ')[1].split('Описание:')[0]
    await state.set_state(GetTransferPhoto.GET_PHOTO)


async def back_to_schools(callback: types.CallbackQuery):
    await callback.message.answer("Выберите школу, в которой учится ваш ребенок",
                         reply_markup=generate_schools_ikb(get_school_list()))
    await callback.message.delete()


async def back_to_classes(callback: types.CallbackQuery):
    global school_const
    await callback.message.answer("Выберите класс, в котором учится ваш ребенок",
                                     reply_markup=generate_classes_ikb(school_const, get_classes_list(school_const)))
    await callback.message.delete()
