import textwrap
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from database.db_message import get_messages, get_message


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
    rent_callback = CallbackData("ri_si", "id", "action")
    kb = InlineKeyboardMarkup(resize_keyboard=True)
    for task in tasks:
        button_gen = InlineKeyboardButton(
            f"Name: {task[4]}",
            callback_data=rent_callback.new(id=task[0], action="show"))
        button_del = InlineKeyboardButton(
            "Удалить",
            callback_data=rent_callback.new(id=task[0], action="dele"))
        button_ch = InlineKeyboardButton(
            f"Shedule: {task[3]}",
            callback_data=rent_callback.new(id=task[0], action="ch"))
        kb.add(button_gen)
        kb.add(button_ch)

        if task[1] == 'on':
            button_status = InlineKeyboardButton(
                f"Status: {task[1]}  \U00002705",
                callback_data=rent_callback.new(id=task[0], action="status_off"))
            kb.add(button_del, button_status)
        else:
            button_status = InlineKeyboardButton(
                f"Status: {task[1]}  ⛔",
                callback_data=rent_callback.new(id=task[0], action="status_on"))
            kb.add(button_del, button_status)
    button_back = InlineKeyboardButton(
        "Главное меню",
        callback_data="back_main")
    kb.add(button_back)
    return kb


async def single_info(inst_id):
    msg = await get_message(inst_id)
    status = msg[1]
    rent_callback = CallbackData("ind_ch", "id", "action")
    if status == 'on':
        button_st = InlineKeyboardButton(
            f'Статус: {status}  \U00002705',
            callback_data=rent_callback.new(id=inst_id, action='turn_off'))
    else:
        button_st = InlineKeyboardButton(
            f'Статус: {status}  ⛔',
            callback_data=rent_callback.new(id=inst_id, action='turn_on'))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [button_st],
        [InlineKeyboardButton(f'{msg[3]}', callback_data=rent_callback.new(id=inst_id, action='change_sch'))],
        [InlineKeyboardButton('Удалить', callback_data=rent_callback.new(id=inst_id, action='delete'))],
        [InlineKeyboardButton('Главное меню', callback_data='back_main')]

    ])
    return kb

