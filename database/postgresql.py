import psycopg2
from decouple import config


db = psycopg2.connect(
    host=f"{config('POSTGRES_HOSTNAME')}",
    database=f"{config('POSTGRES_DB')}",
    user=f"{config('POSTGRES_USER')}",
    password=f"{config('POSTGRES_PASSWORD')}",
    port=f"{config('DATABASE_PORT')}"
)

cur = db.cursor()
