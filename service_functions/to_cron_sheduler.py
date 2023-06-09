from datetime import datetime
from aiogram import Bot
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config
from sqlalchemy import create_engine

bot = Bot(config("BOT_TOKEN"), parse_mode="html")

URL = f'postgresql://{config("POSTGRES_USER")}:{config("POSTGRES_PASSWORD")}@{config("POSTGRES_HOSTNAME")}:{config("DATABASE_PORT")}/{config("POSTGRES_DB")}'
engine = create_engine(URL)


scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
scheduler.add_jobstore('sqlalchemy', engine=engine)
jobstore = SQLAlchemyJobStore(engine=engine)


async def test_msg(inst, chat_id, chat_admin_id):
    try:
        print(inst, chat_id, chat_admin_id)
    except Exception as ex:
        print(f"Exception: {ex}")


async def create_test_job(inst, chat_to_send, chat_id, cron_date_dict, job_id, scheduler):
    try:
        date = datetime.now()
        job = scheduler.add_job(
            send_msg,
            'cron',
            id=str(job_id),
            kwargs={"inst": inst, "chat_id": chat_to_send, "chat_admin_id": chat_id},
            start_date=date,
            minute=cron_date_dict['minute'],
            hour=cron_date_dict['hour'],
            day=cron_date_dict['day'],
            month=cron_date_dict['month'],
            day_of_week=cron_date_dict['day_of_week']
        )
        return job
    except Exception as exxxx:
        return(f"1122Ошибка при создании расписания отправки {exxxx}")


async def send_msg(inst, chat_id, chat_admin_id):
    try:
        if 'photo_id' in inst[2].keys():
            await bot.send_photo(chat_id=chat_id, photo=inst[2]['photo_id'], caption=inst[2]['caption'])

        elif 'document_id' in inst[2].keys():
            await bot.send_document(chat_id=chat_id, document=inst[2]['document_id'], caption=inst[2]['caption'])

        else:
            await bot.send_message(chat_id=chat_id, text=f"{inst[2]['caption']}")
    except Exception as exx:
        await bot.send_message(chat_id=chat_admin_id, text=f"Ошибка при отправке сообщения: {exx}")


async def get_cron_date(schedule):
    num_list = schedule.split(' ')
    dict_to_send = {'minute': num_list[0],
                    'hour': num_list[1],
                    'day': num_list[2],
                    'month': num_list[3],
                    'day_of_week': num_list[4]}
    if num_list[2] == 7:
        dict_to_send['day'] = 0
    return dict_to_send


async def create_job(inst, chat_to_send, chat_id, cron_date_dict, job_id, scheduler):
    try:
        date = datetime.now()
        job = scheduler.add_job(
            send_msg,
            'cron',
            id=str(job_id),
            kwargs={"inst": inst, "chat_id": chat_to_send, "chat_admin_id": chat_id},
            start_date=date,
            minute=cron_date_dict['minute'],
            hour=cron_date_dict['hour'],
            day=cron_date_dict['day'],
            month=cron_date_dict['month'],
            day_of_week=cron_date_dict['day_of_week']

        )
        return job
    except Exception as exxxx:
        return(f"11Ошибка при создании расписания отправки {exxxx}")


async def delete_job(job_id):
    try:
        scheduler.remove_job(job_id=str(job_id))
    except Exception as ex:
        print("JOB not DELETED", ex)
