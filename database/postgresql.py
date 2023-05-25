import psycopg2


db = psycopg2.connect(
    host="127.0.0.1",
    database="shedule_mess",
    user="test_user",
    password="sh_mess_pwd",
    port=5432
)

cur = db.cursor()
