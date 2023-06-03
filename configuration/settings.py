import logging

from aiogram import Dispatcher, types
from handlers.commands import register as reg_commands
from handlers.msg_creation import register as reg_msg



logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format=u'[%(asctime)s] - %(message)s')
logger.info("Starting bot")
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start bot")
    ])


def register_handlers(dp: Dispatcher):
    reg_commands(dp)
    reg_msg(dp)
