from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from configuration import settings
import asyncio
from service_functions.to_cron_sheduler import scheduler, bot


async def main():
    settings.logger.info("Bot started.")

    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    scheduler.start()

    settings.register_handlers(dp)

    await settings.set_default_commands(dp)
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
