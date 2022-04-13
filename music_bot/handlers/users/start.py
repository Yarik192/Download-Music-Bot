import psycopg2
from aiogram import types

from keyboards.default.keyboards import menu
from loader import dp


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привет, просто отправь мне название песни, я найду и отправлю её тебе", reply_markup=menu)
    conn = psycopg2.connect(dbname="telegrambot", user="postgres",
                            password="1234", host="localhost")
    cur = conn.cursor()
    cur.execute(f"SELECT username, fullname FROM users WHERE user_id = {message.from_user.id};")
    data = [x for x in cur]
    user = (message.from_user.username, message.from_user.full_name)
    if not data:
        try:
            cur.execute(
                f"INSERT INTO users VALUES('{message.from_user.id}', \
                '@{message.from_user.username}', '{message.from_user.full_name}');")
            conn.commit()
        except Exception as e:
            print(e)
    if user not in data:
        try:
            cur.execute(
                f"UPDATE users SET username = '{message.from_user.username}', \
                fullname = '{message.from_user.full_name}' WHERE user_id = {message.from_user.id}")
            conn.commit()
        except Exception as e:
            print(e)
