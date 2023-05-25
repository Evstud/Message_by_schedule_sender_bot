from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from decouple import config
from keyboards.inline import kb_main_menu


async def bot_start(msg: types.Message, state: FSMContext):
    await state.finish()
    # print(type(config("ADMIN_ID")), type(msg.from_user.id))
    if int(config("ADMIN_ID")) == msg.from_user.id:
        await msg.answer(f"Hello, {msg.from_user.first_name}!", reply_markup=kb_main_menu())
    else:
        await msg.answer(f"You aren't an admin of this group.")


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
