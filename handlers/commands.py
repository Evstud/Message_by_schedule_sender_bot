from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from decouple import config
from keyboards.inline import kb_main_menu
from keyboards.inline import kb_reply_to_users_chat
# from handlers.msg_creation import NewMessage


ADMIN_CHAT_ID = config("ADMIN_ID")


async def bot_start(msg: types.Message, state: FSMContext):
    if msg.chat.type == 'private':
        await state.finish()
        if int(config("ADMIN_ID")) == msg.from_user.id:
            await msg.answer(f"Hello, {msg.from_user.first_name}!", reply_markup=kb_main_menu())
        else:
            message = msg.text
            user_id = msg.from_user.id
            chat_id = msg.chat.id
            await msg.bot.send_message(
                text=f"New message: '{message}'.\n"
                     f"From: {user_id}.",
                chat_id=ADMIN_CHAT_ID,
                reply_markup=await kb_reply_to_users_chat(users_chat=chat_id)
            )
            await msg.answer(f"You aren't an admin of this group.")
    else:
        await msg.answer('Этот чат не приватный.')


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
