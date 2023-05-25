from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from decouple import config
from keyboards.inline import kb_main_menu


async def bot_start(msg: types.Message, state: FSMContext):
    if msg.chat.type == 'private':
        await state.finish()
        if int(config("ADMIN_ID")) == msg.from_user.id:
            await msg.answer(f"Hello, {msg.from_user.first_name}!", reply_markup=kb_main_menu())
        else:
            await msg.answer(f"You aren't an admin of this group.")
    else:
        await msg.answer('Этот чат не приватный.')


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
