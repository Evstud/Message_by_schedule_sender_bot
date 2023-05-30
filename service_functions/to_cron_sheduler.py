from datetime import datetime
from aiogram import Bot
from decouple import config
# from bot_main import scheduler


# bot = Bot(config("BOT_TOKEN"), parse_mode="html")


async def send_msg(inst, chat_id, chat_admin_id, bot):
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


async def create_job(inst, chat_to_send, chat_id, cron_date_dict, job_id, scheduler, bot):
    try:
        scheduler.add_job(
            send_msg,
            'cron',
            id=str(job_id),
            kwargs={"inst": inst, "chat_id": chat_to_send, "chat_admin_id": chat_id, "bot": bot},
            start_date=datetime.now(),
            minute=cron_date_dict['minute'],
            hour=cron_date_dict['hour'],
            day=cron_date_dict['day'],
            month=cron_date_dict['month'],
            day_of_week=cron_date_dict['day_of_week']

        )
    except Exception  as exxxx:
        await bot.send_message(chat_id=chat_id, text=f"Job не создана: {exxxx}")


async def delete_job(job_id, scheduler):
    scheduler.remove_job(f"{job_id}")
