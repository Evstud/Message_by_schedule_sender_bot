from aiogram import Dispatcher, types
from decouple import config

from handlers.commands import register as reg_commands
from handlers.msg_creation import register as reg_msg

import logging

logger = logging.getLogger('bot_logger')
logger.setLevel(logging.INFO)

fi_handler = logging.FileHandler(filename='bot.log')
fi_handler.setLevel(logging.INFO)

fi_format = logging.Formatter(
    fmt="%(asctime)s %(levelname)s %(message)s",
    datefmt='%m%d%Y %I:%M:%p'
)
fi_handler.setFormatter(fi_format)

logger.addHandler(fi_handler)


bot_token = config("BOT_TOKEN")


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start bot")
    ])


def register_handlers(dp: Dispatcher):
    reg_commands(dp)
    reg_msg(dp)