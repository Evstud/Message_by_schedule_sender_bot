# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.schedulers.background import BackgroundScheduler
# from decouple import config
# from datetime import timedelta, datetime
# # from sqlalchemy import create_engine
#
#
# def hello():
#     print("In a timely fashion!")
#
#
# URL = f'postgresql:///{config("POSTGRES_USER")}:{config("POSTGRES_PASSWORD")}@{config("POSTGRES_HOSTNAME")}:{config("DATABASE_PORT")}/{config("POSTGRES_DB")}'
#
# # engine = create_engine(URL)
#
# # schedular = AsyncIOScheduler()
# schedular = BackgroundScheduler()
# schedular.add_jobstore('sqlalchemy', url=f'postgresql://{config("POSTGRES_USER")}:{config("POSTGRES_PASSWORD")}@{config("POSTGRES_HOSTNAME")}:{config("DATABASE_PORT")}/{config("POSTGRES_DB")}')
#
# # DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{DATABASE_PORT}/{POSTGRES_DB}"
#
# alarm_time = datetime.now() + timedelta(seconds=5)
# schedular.add_job(hello, run_date=alarm_time)
# schedular.start()


