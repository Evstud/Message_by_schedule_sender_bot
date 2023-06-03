import json
from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import BadRequest
from decouple import config
from bot_main import scheduler
# from bot_main import bot
from keyboards import inline
from database.db_message import (create_message, delete_message, get_message, turn_on, turn_off,
                                 update_schedule, get_messages)
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
        await call.message.edit_text(
            text=f"Hello, {name}!",
            reply_markup=inline.kb_main_menu())
        # await call.message.delete()

        # await NewMessage.prepare_to_save.set()
    except BadRequest:
        # if call.message:
        await call.message.delete()
        await call.message.delete_reply_markup()
        await state.finish()
        name = call.from_user.first_name
        await call.message.answer(
            text=f"Hello, {name}!",
            reply_markup=inline.kb_main_menu())
        await call.message.delete()

        # await NewMessage.prepare_to_save.set()


# async def create_msg_step1(call: types.CallbackQuery):
#     await NewMessage.prepare_to_save.set()
#     await call.message.edit_text("Выберите действие:", reply_markup=inline.kb_save_and_main())


async def create_msg_step1(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    msg = await call.message.edit_text(
        text="Введите название задачи:",
        reply_markup=inline.kb_back_to_main())
    async with state.proxy() as data:
        data['msg_id_to_del1'] = msg.message_id
    await NewMessage.name.set()


async def create_msg_step2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg.text
    await msg.bot.send_message(
        text=f"Название новой задачи: \"{msg.text}\"",
        chat_id=msg.from_id)
    await msg.bot.delete_message(
        chat_id=msg.from_id,
        message_id=data['msg_id_to_del1'])
    await msg.bot.delete_message(
        chat_id=msg.from_id,
        message_id=msg.message_id)
    message = await msg.bot.send_message(
        text="Введите сообщение:",
        chat_id=msg.from_id,
        reply_markup=inline.kb_back_to_main())
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
            await msg.bot.send_photo(
                chat_id=chat_id,
                photo=msg['photo'][0]['file_id'],
                caption=f"{msg['caption']}")
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=data['msg_id_to_del2'])
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=msg.message_id)

        elif 'document' in msg.iter_keys():
            data['msg'] = json.dumps({
                'document_id': msg['document']['file_id'],
                'caption': msg['caption']
            })
            await msg.bot.send_document(
                chat_id=msg.from_id,
                document=msg['document']['file_id'],
                caption=f"{msg['caption']}")
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=data['msg_id_to_del2'])
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=msg.message_id)
            # await bot.send_document(chat_id=chat_id, document=inst[2]['document_id'], caption=inst[2]['caption'])

        elif 'text' in msg.iter_keys():
            data['msg'] = json.dumps({
                'caption': msg.text
            })
            await msg.bot.send_message(
                chat_id=chat_id,
                text=f"{msg.text}")
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=data['msg_id_to_del2'])
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=msg.message_id)

        message = await msg.bot.send_message(
            text="Введите расписание отправки задачи в 'cron' формате:",
            chat_id=msg.from_id,
            reply_markup=inline.kb_back_to_main())
        data['msg_id_to_del3'] = message.message_id
    await NewMessage.scheduler_.set()


async def create_msg_step4(msg: types.Message, state: FSMContext):
    # cron format validation
    # if len(msg.text.split(' ')) != 5:
    try:
        if len(msg.text.split(' ')) != 5:
            raise Exception("list index out of range")
        cron_date_dict = await get_cron_date(msg.text)
        test_instance = [111, 'off', {'caption': 'test_caption_text'}, cron_date_dict, 'test_name1', 1]
        new_jo = await create_job(
            inst=test_instance,
            chat_to_send=chat_to_send,
            chat_id=chat_id,
            cron_date_dict=cron_date_dict,
            job_id=test_instance[5],
            bot=msg.bot,
            scheduler=scheduler
        )
        # await turn_on(query_params[1])
        # print(new_jo.id)
        scheduler.remove_job(job_id=new_jo.id)
        # print(del_result)
    except Exception as ex:
        await msg.bot.send_message(
            chat_id=chat_id,
            text=f'Ошибка при создании расписания отправки: {ex}')
        message = await msg.bot.send_message(
            text="Введите расписание отправки задачи в 'cron' формате:",
            chat_id=msg.from_id,
            reply_markup=inline.kb_back_to_main())
        async with state.proxy() as data:
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=data['msg_id_to_del3'])
            data['msg_id_to_del3'] = message.message_id
        await msg.bot.delete_message(
            chat_id=msg.from_id,
            message_id=msg.message_id)

    else:
        # try:
        #     scheduler.start()
        # except:
        #     pass
        try:
            async with state.proxy() as data:
                data['schedule'] = msg.text
            await msg.bot.send_message(
                chat_id=msg.from_id,
                text=f"Расписание отправки новой задачи: {data['schedule']}")
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=data['msg_id_to_del3'])
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=msg.message_id)
            message = await msg.bot.send_message(
                chat_id=msg.from_id,
                text=f"Сохранить данную задачу?\n\n",
                reply_markup=inline.kb_yesno())
            async with state.proxy() as data:
                data['msg_id_to_del4'] = message.message_id
            await NewMessage.choice.set()
        except Exception as exx:
            await msg.bot.send_message(
                chat_id=chat_id,
                text=f'Ошибка при создании расписания отправки: {exx}')


async def save_or_not(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        dict_to_save = data.as_dict()
        await call.message.delete_reply_markup()
        # print(dict_to_save)
        if call.data == 'yes':
            try:
                await create_message(dict_to_save)
            except Exception as ex:
                await call.message.edit_text(
                    text=f"Ошибка при создании задачи '{dict_to_save['name']}': {ex}")
            else:
                await call.message.edit_text(
                    text=f"Задача создана: '{dict_to_save['name']}'")
                await call.message.answer(
                    text=f"Выберите действие:",
                    reply_markup=inline.kb_back_after_task_creation())

        elif call.data == 'no':
            await call.message.edit_text(
                text=f"Отмена сохранения задачи: '{dict_to_save['name']}'")
            await call.message.answer(
                text=f"Выберите действие:",
                reply_markup=inline.kb_back_after_task_creation())

    await state.finish()


async def create_another_task(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    message = await call.message.answer(
        "Введите название задачи:",
        reply_markup=inline.kb_back_to_main())
    async with state.proxy() as data:
        data['msg_id_to_del1'] = message.message_id  ## call.message.message_id
    await NewMessage.name.set()


async def all_tasks(call: types.CallbackQuery):
    messages = await get_messages()
    if messages:
        await call.message.answer(
            text="Список задач:",
            reply_markup=await inline.kb_tasks_list())
    else:
        await call.message.answer(
            text="Список задач пуст",
            reply_markup=await inline.kb_tasks_list())
    await call.message.delete_reply_markup()
    await call.message.delete()
    await MessagesHandler.base_st.set()


async def right_side(call: types.CallbackQuery, state: FSMContext):
    try:
        async with state.proxy() as data:
            await call.bot.delete_message(
                chat_id=chat_id,
                message_id=data['message_to_del'])
    except:
        print("No message to del")

    query_params = call.data.split(':')
    inst = await get_message(query_params[1])
    # print(inst)
    if query_params[2] == "show":
        # inst = await get_message(query_params[1])

        if 'photo_id' in inst[2].keys():
            await call.message.delete_reply_markup()
            await call.message.delete()
            await call.bot.send_photo(
                chat_id=chat_id,
                photo=inst[2]['photo_id'],
                caption=inst[2]['caption'])
            await call.bot.send_message(
                chat_id=chat_id,
                text=f"Задача: {inst[4]}",
                reply_markup=await inline.single_info(inst[0]))
            await MessagesHandler.individual.set()
        elif 'document_id' in inst[2].keys():
            await call.message.delete_reply_markup()
            await call.message.delete()
            await call.bot.send_document(
                chat_id=chat_id,
                document=inst[2]['document_id'],
                caption=inst[2]['caption'])
            await call.bot.send_message(
                chat_id=chat_id,
                text=f"Задача: {inst[4]}",
                reply_markup=await inline.single_info(inst[0]))
            await MessagesHandler.individual.set()
        else:
            await call.message.delete_reply_markup()
            await call.message.delete()
            await call.bot.send_message(
                chat_id=chat_id,
                text=f"{inst[2]['caption']}")
            await call.bot.send_message(
                chat_id=chat_id,
                text=f"Задача: {inst[4]}",
                reply_markup=await inline.single_info(inst[0]))
            await MessagesHandler.individual.set()

    elif query_params[2] == "status_on":
        cron_date_dict = await get_cron_date(inst[3])
        try:
            result = await create_job(
                inst=inst,
                chat_to_send=chat_to_send,
                chat_id=chat_id,
                cron_date_dict=cron_date_dict,
                job_id=inst[5],
                bot=call.bot,
                scheduler=scheduler
            )
            if not result:
                raise Exception("Ошибка при создании расписания отправки")
            await turn_on(query_params[1])
            # await change_job_id(query_params[1], new_jo.id)
            # inst2 = await get_message(query_params[1])

            # print(inst2)
            # print(new_jo.id)
        except Exception as ex:
            await call.bot.send_message(
                chat_id=chat_id,
                text=f'Задача не была включена:  {ex}')
        try:
            scheduler.start()
        except:
            pass
        await call.message.delete_reply_markup()
        await call.message.edit_text(f'Включена задача: {inst[4]}')
        messages = await get_messages()
        if messages:
            await call.message.answer(
                text="Список задач:",
                reply_markup=await inline.kb_tasks_list())
        else:
            await call.message.answer(
                text="Список задач пуст",
                reply_markup=await inline.kb_tasks_list())

        # await call.bot.send_message(
        #     chat_id=chat_id,
        #     text=f'Список задач:',
        #     reply_markup=await inline.kb_tasks_list())

    elif query_params[2] == "status_off":
        await turn_off(query_params[1])
        await call.message.delete_reply_markup()
        try:
            await delete_job(
                job_id=inst[5],
                scheduler=scheduler)
            await call.bot.send_message(
                chat_id=chat_id,
                text=f"Выключена задача: '{inst[4]}'")

        except Exception as exxxx:
            await call.bot.send_message(
                chat_id=chat_id,
                text=f"Выключена задача: '{inst[4]}'")
        await call.message.delete()
        messages = await get_messages()
        if messages:
            await call.message.answer(
                text="Список задач:",
                reply_markup=await inline.kb_tasks_list())
        else:
            await call.message.answer(
                text="Список задач пуст",
                reply_markup=await inline.kb_tasks_list())

        # await call.bot.send_message(
        #     chat_id=chat_id,
        #     text=f'Список задач:',
        #     reply_markup=await inline.kb_tasks_list())

    elif query_params[2] == "ch":
        async with state.proxy() as data:
            data['msg_id'] = query_params[1]
            data['old_sche'] = inst[3]
        await call.message.delete_reply_markup()
        await call.message.delete()
        msg_to_del = await call.bot.send_message(
            chat_id=chat_id,
            text="Введите новое расписание:",
            reply_markup=inline.kb_back_to_main())
        async with state.proxy() as data:
            data["message_to_del"] = msg_to_del.message_id

        await MessagesHandler.ch_ind_sch.set()

    elif query_params[2] == "dele":
        try:
            await call.message.delete_reply_markup()
            # await call.message.delete()
            await delete_message(query_params[1])
            try:
                await delete_job(
                    inst[5],
                    scheduler=scheduler)
            except:
                pass
            await call.message.edit_text(
                # chat_id=chat_id,
                text=f"Удалена задача: '{inst[4]}'.")
                # reply_markup=inline.kb_back_to_main())
            messages = await get_messages()
            if messages:
                await call.message.answer(
                    text="Список задач:",
                    reply_markup=await inline.kb_tasks_list())
            else:
                await call.message.answer(
                    text="Список задач пуст",
                    reply_markup=await inline.kb_tasks_list())

            # await call.bot.send_message(
            #     chat_id=chat_id,
            #     text="Список задач",
            #     # reply_markup=inline.kb_back_to_main())
            #     reply_markup=await inline.kb_tasks_list())

        except Exception as exx:
            await call.message.edit_text(f"Ошибка удаления задачи '{inst[4]}': {exx}.")


async def right_side_individual(call: types.CallbackQuery, state: FSMContext):
    query_params = call.data.split(':')
    inst = await get_message(query_params[1])
    if 'turn_off' == query_params[2]:
        await turn_off(query_params[1])
        inst = await get_message(query_params[1])
        await call.message.delete_reply_markup()
        try:
            await delete_job(
                job_id=inst[5],
                scheduler=scheduler)
            await call.message.edit_text(
                text=f"Выключена задача: '{inst[4]}'"
            )
        except Exception as exxxx:
            await call.message.edit_text(
                # chat_id=chat_id,
                text=f"Выключена задача: '{inst[4]}'")
        # await call.message.delete()
        await call.bot.send_message(
            chat_id=chat_id,
            text=f"Задача: '{inst[4]}'",
            reply_markup=await inline.single_info(inst_id=inst[0]))
        # async with state.proxy() as data:
        #     data["message_to_del"] = msg_to_del.message_id

    elif 'turn_on' == query_params[2]:
        cron_date_dict = await get_cron_date(inst[3])
        try:
            new_jo = await create_job(
                inst=inst,
                chat_to_send=chat_to_send,
                chat_id=chat_id,
                cron_date_dict=cron_date_dict,
                job_id=inst[5],
                bot=call.bot,
                scheduler=scheduler
            )
            if not new_jo:
                raise Exception("Ошибка при создании расписания отправки")
            await turn_on(query_params[1])
            await call.bot.send_message(
                chat_id=chat_id,
                text=f"Включена задача: '{inst[4]}'"
            )
            # print(new_jo)
        except Exception as ex:
            await call.bot.send_message(
                chat_id=chat_id,
                text=f"Не включена задача: '{inst[4]}'")
        try:
            scheduler.start()
        except:
            pass
        await call.message.delete_reply_markup()
        # await call.message.delete()
        await call.bot.send_message(
            chat_id=chat_id,
            text=f"Задача: '{inst[4]}'",
            reply_markup=await inline.single_info(inst[0]))
        # async with state.proxy() as data:
        #     data["message_to_del"] = msg_to_del.message_id

    elif 'change_sch' == query_params[2]:
        inst = await get_message(query_params[1])
        async with state.proxy() as data:
            data['msg_id'] = query_params[1]
            data['old_sche'] = inst[3]
        await call.message.delete_reply_markup()
        # await call.message.delete()
        msg_to_del = await call.message.edit_text(
            # chat_id=chat_id,
            text="Введите новое расписание:",
            reply_markup=inline.kb_back_to_main())
        async with state.proxy() as data:
            data["message_to_del"] = msg_to_del.message_id

        await MessagesHandler.ch_ind_sch.set()

    else:
        try:
            await call.message.delete_reply_markup()
            # await call.message.delete()
            await delete_message(query_params[1])
            try:
                await delete_job(
                    inst[5],
                    scheduler=scheduler)
            except Exception as exxx:
                print(f"Job is not deleted: {exxx}")
            await call.bot.send_message(
                # chat_id=chat_id,
                chat_id=chat_id,
                text=f"Удалена задача: '{inst[4]}'")
            print('here')
            messages = await get_messages()
            if messages:
                await call.message.answer(
                    text="Список задач:",
                    reply_markup=await inline.kb_tasks_list())
            else:
                await call.message.answer(
                    text="Список задач пуст",
                    reply_markup=await inline.kb_tasks_list())

            # await call.bot.send_message(
            #     chat_id=chat_id,
            #     text="Список задач:",
            #     reply_markup=await inline.kb_tasks_list())
            print('and here')
            # async with state.proxy() as data:
            #     data["message_to_del"] = msg_to_del.message_id
            await call.message.delete()

        except Exception as exx:
            await call.message.edit_text(f"Ошибка удаления задачи '{inst[4]}': {exx}")


async def change_schedule1(msg: types.Message, state: FSMContext):
    # cron format validation
    # if len(msg.text.split(' ')) != 5:

    async with state.proxy() as data:
        try:
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=data['message_to_del'])
        except:
            print("No msg to delete")
            pass
        try:
            await msg.bot.delete_message(
                chat_id=msg.from_id,
                message_id=data['message_to_del_sche'])
        except:
            print("No msg to delete")
            pass
    try:
        if len(msg.text.split(' ')) != 5:
            raise Exception("list index out of range")
        cron_date_dict = await get_cron_date(msg.text)
        test_instance = [111, 'off', {'caption': 'test_caption_text'}, cron_date_dict, 'test_name1', 1]
        new_jo = await create_job(
            inst=test_instance,
            chat_to_send=chat_to_send,
            chat_id=chat_id,
            cron_date_dict=cron_date_dict,
            job_id=test_instance[5],
            bot=msg.bot,
            scheduler=scheduler
        )
        # await turn_on(query_params[1])
        # print(new_jo.id)
        scheduler.remove_job(job_id=new_jo.id)
        # print(del_result)
    except Exception as ex:
        # await msg.delete_reply_markup()
        # await msg.delete()

        await msg.bot.send_message(
            chat_id=chat_id,
            text=f'Ошибка при создании расписания отправки: {ex}')
        # await msg.delete_reply_markup()
        # await msg.delete()
        msg_to_del = await msg.bot.send_message(
            chat_id=chat_id,
            text="Введите новое расписание:",
            reply_markup=inline.kb_back_to_main())
        # await msg.bot.delete_message(
        #     chat_id=msg.from_id,
        #     message_id=msg.message_id)
        await msg.delete()
        async with state.proxy() as data:
            data['message_to_del_sche'] = msg_to_del.message_id

    else:
        # await msg.bot.delete_message(
        #     chat_id=msg.from_id,
        #     message_id=msg.message_id)

        async with state.proxy() as data:
            data['new_sche'] = msg.text
            await msg.answer(
                text=f"Сохранить измененное расписание?\n\n"
                     f"Прежнее расписание: {data['old_sche']},\n"
                     f"Новое расписание: {data['new_sche']}.",
                reply_markup=inline.kb_yesno())
            await MessagesHandler.ch_ind_sch_y_n.set()
        # await msg.delete_reply_markup()
        await msg.delete()


async def change_schedule2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        try:
            inst = await get_message(data['msg_id'])
            if call.data == 'yes':
                await update_schedule(data['msg_id'], data['new_sche'])

                try:
                    await delete_job(
                        inst[5],
                        scheduler=scheduler)
                except:
                    pass
                if inst[1] == 'on':
                    await turn_off(inst[0])
                    # cron_date_dict = await get_cron_date(data['new_sche'])
                    # await create_job(inst, chat_to_send, chat_id, cron_date_dict, inst[5])
                await call.message.edit_text(
                    text=f"Изменение расписания задачи '{inst[4]}'")
                await call.bot.send_message(
                    chat_id=chat_id,
                    text="Возврат в главное меню",
                    reply_markup=inline.kb_back_to_main())
            else:
                await call.message.edit_text(
                    text=f"Отмена изменения расписания задачи '{inst[4]}'")
                await call.bot.send_message(
                    chat_id=chat_id,
                    text="Возврат в главное меню",
                    reply_markup=inline.kb_back_to_main())

        except Exception as exx:
            await call.message.edit_text(
                text=f"Ошибка изменения расписания задачи '{inst[4]}': {exx}")
            await call.bot.send_message(
                chat_id=chat_id,
                text="Возврат в главное меню",
                reply_markup=inline.kb_back_to_main())

    await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(main_menu_button, text='back_main', state='*')
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


