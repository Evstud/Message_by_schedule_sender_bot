import json
from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import BadRequest
from decouple import config
# from bot_main import scheduler
from bot_main import bot
from keyboards import inline
from database.db_message import (create_message, delete_message, get_message, turn_on, turn_off,
                                 update_schedule)
from service_functions.to_cron_sheduler import get_cron_date, create_job, delete_job

# bot = Bot(config("BOT_TOKEN"), parse_mode="html")
chat_to_send = config("GROUP_ID")
chat_id = config("ADMIN_ID")


class NewMessage(StatesGroup):
    # prepare_to_save = State()
    name = State()
    body = State()
    scheduler_ = State()
    choice = State()


class MessagesHandler(StatesGroup):
    base_st = State()
    individual = State()
    ch_ind_sch_y_n = State()
    ch_ind_sch = State()


async def main_menu_button(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete_reply_markup()
        await state.finish()
        name = call.from_user.first_name
        await call.message.answer(f"Hello, {name}!", reply_markup=inline.kb_main_menu())
        await call.message.delete()

        # await NewMessage.prepare_to_save.set()
    except BadRequest:
        # if call.message:
        #     await call.message.delete()
        await call.message.delete_reply_markup()
        await state.finish()
        name = call.from_user.first_name
        await call.message.answer(f"Hello, {name}!", reply_markup=inline.kb_main_menu())
        await call.message.delete()

        # await NewMessage.prepare_to_save.set()


# async def create_msg_step1(call: types.CallbackQuery):
#     await NewMessage.prepare_to_save.set()
#     await call.message.edit_text("Выберите действие:", reply_markup=inline.kb_save_and_main())


async def create_msg_step1(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    msg = await call.message.edit_text("Введите название задачи:", reply_markup=inline.kb_back_to_main())
    async with state.proxy() as data:
        data['msg_id_to_del1'] = msg.message_id
    await NewMessage.name.set()


async def create_msg_step2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg.text
    await bot.send_message(text=f"Название новой задачи: \"{msg.text}\"", chat_id=msg.from_id)
    await bot.delete_message(chat_id=msg.from_id, message_id=data['msg_id_to_del1'])
    await bot.delete_message(chat_id=msg.from_id, message_id=msg.message_id)
    message = await bot.send_message(text="Введите сообщение:", chat_id=msg.from_id, reply_markup=inline.kb_back_to_main())
    async with state.proxy() as data:
        data['msg_id_to_del2'] = message.message_id
    await NewMessage.body.set()


async def create_msg_step3(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'photo' in msg.iter_keys():
            data['msg'] = json.dumps({
                'photo_id': msg['photo'][0]['file_id'],
                'caption': msg['caption']
            })
            await bot.send_photo(chat_id=chat_id, photo=msg['photo'][0]['file_id'], caption=f"Текст сообщения новой задачи: {msg['caption']}")
            await bot.delete_message(chat_id=msg.from_id, message_id=data['msg_id_to_del2'])
            await bot.delete_message(chat_id=msg.from_id, message_id=msg.message_id)

        elif 'document' in msg.iter_keys():
            data['msg'] = json.dumps({
                'document_id': msg['document']['file_id'],
                'caption': msg['caption']
            })
            await bot.send_document(chat_id=msg.from_id, document=msg['document']['file_id'], caption=f"Текст сообщения новой задачи: {msg['caption']}")
            await bot.delete_message(chat_id=msg.from_id, message_id=data['msg_id_to_del2'])
            await bot.delete_message(chat_id=msg.from_id, message_id=msg.message_id)
            # await bot.send_document(chat_id=chat_id, document=inst[2]['document_id'], caption=inst[2]['caption'])

        elif 'text' in msg.iter_keys():
            data['msg'] = json.dumps({
                'caption': msg.text
            })
            await bot.send_message(chat_id=chat_id, text=f"Текст сообщения новой задачи: {msg.text}")
            await bot.delete_message(chat_id=msg.from_id, message_id=data['msg_id_to_del2'])
            await bot.delete_message(chat_id=msg.from_id, message_id=msg.message_id)

        message = await bot.send_message(text="Введите расписание отправки задачи в 'cron' формате:", chat_id=msg.from_id, reply_markup=inline.kb_back_to_main())
        data['msg_id_to_del3'] = message.message_id
    await NewMessage.scheduler_.set()


async def create_msg_step4(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['schedule'] = msg.text
    await bot.send_message(chat_id=msg.from_id, text=f"Расписание отправки новой задачи: {data['schedule']}")
    await bot.delete_message(chat_id=msg.from_id, message_id=data['msg_id_to_del3'])
    await bot.delete_message(chat_id=msg.from_id, message_id=msg.message_id)
    message = await bot.send_message(chat_id=msg.from_id, text=f"Сохранить данную задачу?\n\n",
                     # f"Название задачи: {data['name']},\n"
                     # f"Текст: {json.loads(data['msg'])['caption']},\n"
                     # f"Расписание отправки: {data['schedule']}.",
                                     reply_markup=inline.kb_yesno())
    async with state.proxy() as data:
        data['msg_id_to_del4'] = message.message_id
    await NewMessage.choice.set()


async def save_or_not(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        dict_to_save = data.as_dict()
        await call.message.delete_reply_markup()
        # print(dict_to_save)
        if call.data == 'yes':
            try:
                await create_message(dict_to_save)
            except Exception as ex:
                await call.message.edit_text(f"Задача '{dict_to_save['name']}' не создана: {ex}")
            else:
                await call.message.edit_text(f"Задача '{dict_to_save['name']}' успешно создана.",
                                             reply_markup=inline.kb_back_after_task_creation())

        elif call.data == 'no':
            await call.message.edit_text(f"Сохранение задачи '{dict_to_save['name']}' отменено.",
                                         reply_markup=inline.kb_back_after_task_creation())

    await state.finish()


async def create_another_task(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    message = await call.message.answer("Введите название задачи:")
    async with state.proxy() as data:
        data['msg_id_to_del1'] = message.message_id  ## call.message.message_id
    await NewMessage.name.set()


async def all_tasks(call: types.CallbackQuery):
    await call.message.answer("Список задач:", reply_markup=await inline.kb_tasks_list())
    await MessagesHandler.base_st.set()


async def right_side(call: types.CallbackQuery, state: FSMContext):
    query_params = call.data.split(':')
    inst = await get_message(query_params[1])
    if query_params[2] == "show":
        if 'photo_id' in inst[2].keys():
            await call.message.delete_reply_markup()
            await call.message.delete()
            await bot.send_photo(chat_id=chat_id, photo=inst[2]['photo_id'], caption=inst[2]['caption'])
            await bot.send_message(chat_id=chat_id, text=f"Расписание: {inst[3]} Статус: {inst[1]}",
                                   reply_markup=inline.single_info(inst[1], inst[0]))
            await MessagesHandler.individual.set()
        elif 'document_id' in inst[2].keys():
            await call.message.delete_reply_markup()
            await call.message.delete()
            await bot.send_document(chat_id=chat_id, document=inst[2]['document_id'], caption=inst[2]['caption'])
            await bot.send_message(chat_id=chat_id, text=f"Расписание: {inst[3]}\n Статус: {inst[1]}",
                                   reply_markup=inline.single_info(inst[1], inst[0]))
            await MessagesHandler.individual.set()
        else:
            await call.message.delete_reply_markup()
            await call.message.delete()
            await bot.send_message(chat_id=chat_id, text=f"{inst[2]['caption']}")
            await bot.send_message(chat_id=chat_id, text=f"Расписание: {inst[3]}\n Статус: {inst[1]}",
                                   reply_markup=inline.single_info(inst[1], inst[0]))
            await MessagesHandler.individual.set()

    elif query_params[2] == "status_on":
        await turn_on(query_params[1])
        cron_date_dict = await get_cron_date(inst[3])
        try:
            await create_job(
                inst=inst,
                chat_to_send=chat_to_send,
                chat_id=chat_id,
                cron_date_dict=cron_date_dict,
                job_id=inst[5]
            )
        except Exception as ex:
            await bot.send_message(chat_id=chat_id, text=f'Exception при создании job расписания {ex}')
        try:
            scheduler.start()
        except:
            pass
        await call.message.delete_reply_markup()
        await call.message.delete()
        await bot.send_message(chat_id=chat_id, text=f'Список задач:', reply_markup=await inline.kb_tasks_list())

    elif query_params[2] == "status_off":
        await turn_off(query_params[1])
        await call.message.delete_reply_markup()
        try:
            await delete_job(job_id=inst[5])
        except Exception as exxxx:
            await bot.send_message(chat_id=chat_id, text=f"Job doesn't deleted: {exxxx}")
        await call.message.delete()
        await bot.send_message(chat_id=chat_id, text=f'Список задач:', reply_markup=await inline.kb_tasks_list())

    elif query_params[2] == "ch":
        async with state.proxy() as data:
            data['msg_id'] = query_params[1]
            data['old_sche'] = inst[3]
        await call.message.delete_reply_markup()
        await call.message.delete()
        await bot.send_message(chat_id=chat_id, text="Введите новое расписание: ")
        await MessagesHandler.ch_ind_sch.set()

    elif query_params[2] == "dele":
        try:
            await call.message.delete_reply_markup()
            await call.message.delete()
            await delete_message(query_params[1])
            try:
                await delete_job(inst[5])
            except:
                pass
            await bot.send_message(chat_id=chat_id, text=f"Задача удалена.",
                                   reply_markup=inline.kb_back_to_main())
        except Exception as exx:
            await call.message.edit_text(f"Задача не удалена, по причине: {exx}.")


async def right_side_individual(call: types.CallbackQuery, state: FSMContext):
    query_params = call.data.split(':')
    inst = await get_message(query_params[1])
    if 'turn_off' == query_params[2]:
        await turn_off(query_params[1])
        inst = await get_message(query_params[1])
        try:
            await delete_job(job_id=inst[5])
        except Exception as exxxx:
            await bot.send_message(chat_id=chat_id, text=f"Job doesn't deleted: {exxxx}")
        await call.message.delete_reply_markup()
        await call.message.delete()
        await bot.send_message(chat_id=chat_id, text=f"Расписание: {inst[3]}\n Статус: {inst[1]}",
                               reply_markup=inline.single_info(inst[1], inst[0]))

    elif 'turn_on' == query_params[2]:
        await turn_on(query_params[1])
        cron_date_dict = await get_cron_date(inst[3])
        try:
            await create_job(
                inst=inst,
                chat_to_send=chat_to_send,
                chat_id=chat_id,
                cron_date_dict=cron_date_dict,
                job_id=inst[5]
            )
        except Exception as ex:
            await bot.send_message(chat_id=chat_id, text=f"Job не создана: {ex}")
        try:
            scheduler.start()
        except:
            pass
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
            try:
                await delete_job(inst[5])
            except:
                pass
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
                inst = await get_message(data['msg_id'])
                try:
                    await delete_job(inst[5])
                except:
                    pass
                if inst[1] == 'on':
                    cron_date_dict = await get_cron_date(data['new_sche'])
                    await create_job(inst, chat_to_send, chat_id, cron_date_dict, inst[5])
                await call.message.answer('Расписание изменено.', reply_markup=inline.kb_back_to_main())
            else:
                await call.message.answer('Изменение расписания отменено.', reply_markup=inline.kb_back_to_main())
        except Exception as exx:
            await call.message.answer(f'Расписание не изменено по причине: {exx}',
                                      reply_markup=inline.kb_back_to_main())
    await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(main_menu_button, text='back_main', state='*')
    # dp.register_callback_query_handler(create_msg_step1, text='create_msg')
    dp.register_callback_query_handler(create_msg_step1, text='create_msg')
    dp.register_message_handler(create_msg_step2, state=NewMessage.name)
    dp.register_message_handler(create_msg_step3, content_types=[
        'photo', 'text', 'audio', 'document', 'sticker', 'voice', 'location', 'contact', 'new_chat_members',
        'pinned_message', 'web_app_data'], state=NewMessage.body)
    dp.register_message_handler(create_msg_step4, state=NewMessage.scheduler_)
    dp.register_callback_query_handler(save_or_not, text=['yes', 'no'], state=NewMessage.choice)
    dp.register_callback_query_handler(create_another_task, text='another_task')
    dp.register_callback_query_handler(all_tasks, text='all_msgs')
    dp.register_callback_query_handler(right_side, state=MessagesHandler.base_st)
    dp.register_callback_query_handler(right_side_individual, state=MessagesHandler.individual)
    dp.register_message_handler(change_schedule1, state=MessagesHandler.ch_ind_sch)
    dp.register_callback_query_handler(change_schedule2, state=MessagesHandler.ch_ind_sch_y_n)


