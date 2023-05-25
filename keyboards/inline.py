from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from database.db_message import (create_message, delete_message, get_message,
                                 get_messages)


def kb_main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Создать задачу', callback_data='create_msg')],
        [InlineKeyboardButton('Все задачи', callback_data='all_msgs')]
    ])
    return kb


def kb_back_to_main() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Главное меню', callback_data='back_main')]
    ])
    return kb


def kb_save_and_main() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Сохранить', callback_data='save')],
        [InlineKeyboardButton('Главное меню', callback_data='back_main')]
    ])
    return kb


def kb_yesno() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Да', callback_data='yes')],
        [InlineKeyboardButton('Нет', callback_data='no')]
    ])
    return kb


def kb_back_after_task_creation() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Создать другую задачу', callback_data='another_task')],
        [InlineKeyboardButton('Главное меню', callback_data='back_main')]
    ])
    return kb


async def kb_tasks_list() -> InlineKeyboardMarkup:
    tasks = await get_messages()
    # print(tasks)
    rent_callback = CallbackData("ri_si", "id", "action")
    kb = InlineKeyboardMarkup()
    for task in tasks:
        # print('000', task[1])
        button_gen = InlineKeyboardButton(f"Name: {task[4]},\nStatus: {task[1]},\nSchedule: {task[3]}.\n",
                                          callback_data=rent_callback.new(id=task[0], action="general"))
        # print(rent_callback.new(id=task[0], action="general"))
        kb.add(button_gen)
        # print(task[1])
        if task[1] == 'on':
            # print(task[0])
            button_show = InlineKeyboardButton("Показать", callback_data=rent_callback.new(id=task[0], action="show"))
            button_status = InlineKeyboardButton("Выключить", callback_data=rent_callback.new(id=task[0], action="status"))
            kb.add(button_show, button_status)

        # elif task[1] == 'off':
        else:
            button_show = InlineKeyboardButton("Показать", callback_data=rent_callback.new(id=task[0], action="show"))
            button_status = InlineKeyboardButton("Выключить", callback_data=rent_callback.new(id=task[0], action="status"))
            kb.add(button_show, button_status)
        button_ch = InlineKeyboardButton("Изменить расписание", callback_data=rent_callback.new(id=task[0], action="ch"))
        button_del = InlineKeyboardButton("Удалить", callback_data=rent_callback.new(id=task[0], action="dele"))
        # kb.add(button_gen, button_show, button_status, button_ch, button_del)
        kb.add(button_ch, button_del)
    button_back = InlineKeyboardButton("Главное меню", callback_data="back_main")
    kb.add(button_back)
    # print(kb)
    return kb


def single_info(status, inst_id):
    rent_callback = CallbackData("ind_ch", "id", "action")

    if status == 'on':
        button_st = InlineKeyboardButton('Выключить', callback_data=rent_callback.new(id=inst_id, action='turn_off'))
    else:
        button_st = InlineKeyboardButton('Включить', callback_data=rent_callback.new(id=inst_id, action='turn_on'))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [button_st],
        [InlineKeyboardButton('Изменить расписание', callback_data=rent_callback.new(id=inst_id, action='change_sch'))],
        [InlineKeyboardButton('Удалить', callback_data=rent_callback.new(id=inst_id, action='delete'))],
        [InlineKeyboardButton('Главное меню', callback_data='back_main')]

    ])
    return kb

