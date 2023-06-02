from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from configuration import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config
import asyncio


# bot = Bot(config("BOT_TOKEN"), parse_mode="html")
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def main():
    settings.logger.info("Bot started.")

    bot = Bot(config("BOT_TOKEN"), parse_mode="html")
    # bot = Bot(settings.bot_token, parse_mode="html")
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    settings.register_handlers(dp)
    await settings.set_default_commands(dp)
    await dp.start_polling()
    scheduler.start()


if __name__ == "__main__":
    asyncio.run(main())
