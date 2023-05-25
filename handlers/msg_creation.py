import json

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import BadRequest
from decouple import config

from aiogram import Bot, Dispatcher

from keyboards import inline
# from database.db_message import create_message
from database.db_message import (create_message, delete_message, get_message, turn_on, turn_off,
                                 update_schedule)
from aiogram.utils.callback_data import CallbackData
from configuration import settings



bot = Bot(config("BOT_TOKEN"), parse_mode="html")


class NewMessage(StatesGroup):
    prepare_to_save = State()
    name = State()
    body = State()
    scheduler = State()
    choice = State()


class MessagesHandler(StatesGroup):
    base_st = State()
    individual = State()
    ch_ind_sch_y_n = State()
    ch_ind_sch = State()


async def main_menu_button(call: types.CallbackQuery, state: FSMContext):
    print('ko')
    try:
        await call.message.delete()
        await call.message.delete_reply_markup()
        await state.finish()
        name = call.from_user.first_name
        await call.message.answer(f"Hello, {name}!", reply_markup=inline.kb_main_menu())
    except BadRequest:
        await state.finish()
        name = call.from_user.first_name
        await call.message.answer(f"Hello, {name}!", reply_markup=inline.kb_main_menu())


async def create_msg_step1(call: types.CallbackQuery, state: FSMContext):
    await NewMessage.prepare_to_save.set()
    await call.message.edit_text("Выберите действие:", reply_markup=inline.kb_save_and_main())


async def create_msg_step2(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите название задачи:")
    await NewMessage.name.set()


async def create_msg_step3(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # print(msg)
        data['name'] = msg.text
    await msg.answer("Введите сообщение: ")
    await NewMessage.body.set()


async def create_msg_step4(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'document' in msg.iter_keys():
            data['msg'] = json.dumps({
                'document_id': msg['document']['file_id'],
                'caption': msg['caption']
            })
            # print(data)
        elif 'photo' in msg.iter_keys():
            data['msg'] = json.dumps({
                'photo_id': msg['photo'][0]['file_id'],
                'caption': msg['caption']
            })

            # print(data)
        elif 'text' in msg.iter_keys():
            # print('text')
            data['msg'] = json.dumps({
                'caption': msg.text
            })
    await msg.answer("Введите расписание отправки задачи ('cron' формате): ")
    await NewMessage.scheduler.set()


async def create_msg_step5(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['schedule'] = msg.text
        # print(data)
        await msg.answer(f"Сохранить данную задачу?\n\n"
                         f"Название задачи: {data['name']},\n"
                         f"Текст: {json.loads(data['msg'])['caption']},\n"
                         f"Расписание отправки: {data['schedule']}.", reply_markup=inline.kb_yesno())
        await NewMessage.choice.set()


async def save_or_not(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        dict_to_save = data.as_dict()
        print(dict_to_save)
        if call.data == 'yes':
            try:
                print('lllsssnnn')
                await create_message(dict_to_save)
            except Exception as ex:
                await call.message.edit_text(f"Задача не сохранена: {ex}")
            else:
                await call.message.edit_text("Задача успешно сохранена.", reply_markup=inline.kb_back_after_task_creation())

        elif call.data == 'no':
            await call.message.edit_text("Сохранение задачи отменено.", reply_markup=inline.kb_back_after_task_creation())
            print('no')

    await state.finish()
    # else:
    #     print(call.data)


async def create_another_task(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите название задачи:")
    await NewMessage.name.set()


async def all_tasks(call: types.CallbackQuery):
    await call.message.answer("Список задач:", reply_markup=await inline.kb_tasks_list())
    await MessagesHandler.base_st.set()




async def right_side(call: types.CallbackQuery):
    query_params = call.data.split(':')
    chat_id = call.message.chat.id
    if query_params[2] == "show":
        inst = await get_message(query_params[1])
        if 'photo_id' in inst[2].keys():
            await call.message.delete_reply_markup()
            await call.message.delete()
            await bot.send_photo(chat_id=chat_id, photo=inst[2]['photo_id'], caption=inst[2]['caption'])
            await bot.send_message(chat_id=chat_id, text=f"Расписание: {inst[3]} Статус: {inst[1]}", reply_markup=inline.single_info(inst[1], inst[0]))
            await MessagesHandler.individual.set()
        elif 'document_id' in inst[2].keys():
            await call.message.delete_reply_markup()
            await call.message.delete()
            await bot.send_document(chat_id=chat_id, document=inst[2]['document_id'], caption=inst[2]['caption'])
            await bot.send_message(chat_id=chat_id, text=f"Расписание: {inst[3]}\n Статус: {inst[1]}", reply_markup=inline.single_info(inst[1], inst[0]))
            await MessagesHandler.individual.set()
        else:
            await call.message.delete_reply_markup()
            await call.message.delete()
            await bot.send_message(chat_id=chat_id, text=f"Текст сообщения: {inst[2]['caption']}")
            await bot.send_message(chat_id=chat_id, text=f"Расписание: {inst[3]}\n Статус: {inst[1]}", reply_markup=inline.single_info(inst[1], inst[0]))
            await MessagesHandler.individual.set()

            print('ok text')

        # await call.message.re
        # await call.message.answer("second")
    elif query_params[2] == "status":
        pass
    elif query_params[2] == "ch":
        pass
    elif query_params[2] == "dele":
        pass


async def right_side_individual(call: types.CallbackQuery, state: FSMContext):
    # turn_off, turn_on, change_sch, delete
    print(call.data)
    query_params = call.data.split(':')
    chat_id = call.message.chat.id
    if 'turn_off' == query_params[2]:
        await turn_off(query_params[1])
        inst = await get_message(query_params[1])
        await call.message.delete_reply_markup()
        await call.message.delete()
        await bot.send_message(chat_id=chat_id, text=f"Расписание: {inst[3]}\n Статус: {inst[1]}",
                               reply_markup=inline.single_info(inst[1], inst[0]))

    elif 'turn_on' == query_params[2]:
        await turn_on(query_params[1])
        inst = await get_message(query_params[1])
        await call.message.delete_reply_markup()
        await call.message.delete()
        await bot.send_message(chat_id=chat_id, text=f"Расписание: {inst[3]}\n"
                                                     f"Статус: {inst[1]}",
                               reply_markup=inline.single_info(inst[1], inst[0]))

    elif 'change_sch' == query_params[2]:
        inst = await get_message(query_params[1])
        async with state.proxy() as data:
            data['msg_id'] = query_params[1]
            data['old_sche'] = inst[3]
        await call.message.delete_reply_markup()
        await call.message.delete()
        await bot.send_message(chat_id=chat_id, text="Введите новое расписание: ")
        await MessagesHandler.ch_ind_sch.set()

    else:

        try:
            await call.message.delete_reply_markup()
            await call.message.delete()
            await delete_message(query_params[1])
            await bot.send_message(chat_id=chat_id, text=f"Задача удалена.",
                                   reply_markup=inline.kb_back_to_main())

        except Exception as exx:
            await call.message.edit_text(f"Задача не удалена, по причине: {exx}.")


async def change_schedule1(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['new_sche'] = msg.text
        await msg.answer(f"Сохранить измененное расписание?\n\n"
                         f"Прежнее расписание: {data['old_sche']},\n"
                         f"Новое расписание: {data['new_sche']},\n", reply_markup=inline.kb_yesno())
        await MessagesHandler.ch_ind_sch_y_n.set()


async def change_schedule2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        try:
            if call.data == 'yes':
                await update_schedule(data['msg_id'], data['new_sche'])
                await call.message.answer('Расписание изменено.', reply_markup=inline.kb_back_to_main())
            else:
                await call.message.answer('Изменение расписания отменено.', reply_markup=inline.kb_back_to_main())
        except Exception as exx:
            await call.message.answer(f'Расписание не изменено по причине: {exx}', reply_markup=inline.kb_back_to_main())



def register(dp: Dispatcher):
    dp.register_callback_query_handler(main_menu_button, text='back_main', state='*')
    dp.register_callback_query_handler(create_msg_step1, text='create_msg')
    dp.register_callback_query_handler(create_msg_step2, text='save', state=NewMessage.prepare_to_save)
    dp.register_message_handler(create_msg_step3, state=NewMessage.name)
    dp.register_message_handler(create_msg_step4, content_types=[
        'photo', 'text', 'audio', 'document', 'sticker', 'voice', 'location', 'contact', 'new_chat_members',
        'pinned_message', 'web_app_data'], state=NewMessage.body)
    dp.register_message_handler(create_msg_step5, state=NewMessage.scheduler)
    dp.register_callback_query_handler(save_or_not, text=['yes', 'no'], state=NewMessage.choice)
    dp.register_callback_query_handler(create_another_task, text='another_task')
    dp.register_callback_query_handler(all_tasks, text='all_msgs')
    dp.register_callback_query_handler(right_side, state=MessagesHandler.base_st)
    dp.register_callback_query_handler(right_side_individual, state=MessagesHandler.individual)
    dp.register_message_handler(change_schedule1, state=MessagesHandler.ch_ind_sch)
    dp.register_callback_query_handler(change_schedule2, state=MessagesHandler.ch_ind_sch_y_n)


