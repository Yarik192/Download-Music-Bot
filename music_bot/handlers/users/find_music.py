import os

from youtubesearchpython import searchYoutube
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.users.functions import download_from_utube, slugify
from loader import dp, bot


@dp.callback_query_handler(lambda c: c.data.startswith("download"))
async def index_music(callback: types.CallbackQuery):
    link = callback.data.replace("download", "")
    path = download_from_utube(link)
    add_to_playlist = InlineKeyboardMarkup()
    add_to_playlist.add(InlineKeyboardButton(text="Добавить в плейлист", callback_data=f"link to playlist:{link}"))
    try:
        with open(path, "rb") as audio:
            await bot.answer_callback_query(callback.id, text="Успешно")
            await bot.send_audio(callback.from_user.id, audio, reply_markup=add_to_playlist)
            os.remove(path)
    except TypeError:
        await bot.send_message(chat_id=callback.from_user.id, text="Время действия запроса исткело")


@dp.message_handler()
async def find_first_result(message: types.Message):
    inline = InlineKeyboardMarkup()
    count = 0
    search = searchYoutube(message.text, mode="dict").result().get("search_result")
    for i in search:
        duration = i.get("duration").split(":")
        try:
            if len(duration) < 3 and int(duration[0]) < 20:
                count += 1
                inline.add(InlineKeyboardButton(f"{slugify(i.get('title'))}", callback_data=f"download{i.get('link')}"))
        except ValueError:
            continue
    if count != 0:
        await message.answer("Поиск...🔎")
        await message.answer(f"Найдено: {count} песен", reply_markup=inline)
    else:
        await message.answer("По вашему запросу ничего не найдено, убедитесь в правильности названия")
