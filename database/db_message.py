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


# async def update_messages(data, msg_id):
#     status = data.get('status')
#     body = data.get('body')
#     cur.execute("UPDATE message SET status = %s, body = %s WHERE id = %s", (status, body, msg_id))


async def delete_message(msg_id):
    cur.execute("DELETE FROM message WHERE id = %s", (msg_id,))
    db.commit()


async def turn_on(msg_id):
    cur.execute("UPDATE message SET status = 'on' WHERE id = %s", (msg_id,))
    db.commit()


async def turn_off(msg_id):
    cur.execute("UPDATE message SET status = 'off' WHERE id = %s", (msg_id,))
    db.commit()


async def update_schedule(msg_id, sche):
    cur.execute("UPDATE message SET schedule = %s WHERE id = %s", (sche, msg_id))
    db.commit()



# async def update_msg_body(msg_id, body):
#     cur.execute("UPDATE message SET body = %s WHERE id = %s", (body, msg_id))

