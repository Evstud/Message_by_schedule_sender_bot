from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from configuration import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio


scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def main():
    settings.logger.info("Bot started.")

    bot = Bot(settings.bot_token, parse_mode="html")
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    settings.register_handlers(dp)
    await settings.set_default_commands(dp)
    await dp.start_polling()
    scheduler.start()


if __name__ == "__main__":
    asyncio.run(main())
