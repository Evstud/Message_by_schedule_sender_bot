from aiogram import Dispatcher, types
from decouple import config

from handlers.commands import register as reg_commands
from handlers.msg_creation import register as reg_msg

import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format=u'[%(asctime)s] - %(message)s')
logger.info("Starting bot")

# bot_token = config("BOT_TOKEN")


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start bot")
    ])


def register_handlers(dp: Dispatcher):
    reg_commands(dp)
    reg_msg(dp)
