from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from configuration import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config
import asyncio
from sqlalchemy import create_engine
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from service_functions.to_cron_sheduler import scheduler, bot


# URL = f'postgresql://{config("POSTGRES_USER")}:{config("POSTGRES_PASSWORD")}@{config("POSTGRES_HOSTNAME")}:{config("DATABASE_PORT")}/{config("POSTGRES_DB")}'
# engine = create_engine(URL)
#
#
# scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
# scheduler.add_jobstore('sqlalchemy', engine=engine)
# jobstore = SQLAlchemyJobStore(engine=engine)

# scheduler.start()


async def main():
    settings.logger.info("Bot started.")

    # bot = Bot(config("BOT_TOKEN"), parse_mode="html")
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    # scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # scheduler.add_jobstore('sqlalchemy', engine=engine)

    print(scheduler._jobstores)

    scheduler.start()

    settings.register_handlers(dp)

    scheduler.print_jobs()

    await settings.set_default_commands(dp)
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
