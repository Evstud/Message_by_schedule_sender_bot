from database.postgresql import db, cur


async def create_message(data):
    cur.execute("INSERT INTO message (name, msg, schedule) VALUES (%s, %s, %s)",
                (data.get('name'), data.get('msg'), data.get('schedule')))
    db.commit()


async def get_messages():
    cur.execute("SELECT * FROM message")
    result = cur.fetchall()
    return result


async def get_message(msg_id):
    cur.execute("SELECT * FROM message WHERE id = %s", (msg_id,))
    result = cur.fetchone()
    return result


async def delete_message(msg_id):
    cur.execute("DELETE FROM message WHERE id = %s", (msg_id,))
    db.commit()


async def turn_on(msg_id):
    cur.execute("UPDATE message SET status = 'on' WHERE id = %s", (msg_id,))
    db.commit()


async def turn_off(msg_id):
    cur.execute("UPDATE message SET status = 'off' WHERE id = %s", (msg_id,))
    db.commit()


# async def change_job_id(msg_id, job_id):
#     cur.execute("UPDATE message SET job_id = %s WHERE id = %s", (job_id, msg_id))


async def update_schedule(msg_id, sche):
    cur.execute("UPDATE message SET schedule = %s WHERE id = %s", (sche, msg_id))
    db.commit()
