from postgresql import db, cur


def create_table_message():
    cur.execute("CREATE TABLE message ("
                "id SERIAL PRIMARY KEY,"
                "status TEXT DEFAULT 'off',"
                "msg JSONB,"
                "schedule TEXT,"
                "name TEXT,"
                "job_id SERIAL)")
    db.commit()


def table_creation():
    create_table_message()


table_creation()
