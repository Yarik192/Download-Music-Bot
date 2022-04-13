import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from pytube import YouTube

from utils.db_api.postgres import conn, cur
from handlers.users.functions import download_from_utube
from keyboards.default.keyboards import join_to_menu, my_or_create, menu
from states.playlists import Create
from loader import dp, bot


@dp.message_handler(lambda m: m.text == "Плейлисты")
async def create_or_choice(message: types.Message):
    await message.answer("Выбери плейлист или создай новый", reply_markup=my_or_create)


@dp.message_handler(lambda m: m.text == "Создать плейлист")
async def create_playlist(message: types.Message):
    await message.answer("Введи название плейлиста", reply_markup=join_to_menu)
    await Create.name.set()


@dp.message_handler(lambda m: m.text == "Мои плейлисты")
async def my_playlists(message: types.Message):
    playlists = InlineKeyboardMarkup()
    cur.execute(f"SELECT name, playlist_id FROM playlists WHERE user_id = {message.from_user.id}")
    data = [x for x in cur]
    if data:
        for i in data:
            playlists.add(InlineKeyboardButton(text=i[0], callback_data=f"playlist_id:{i[-1]}"))
        await message.answer(text="Выбери плейлист", reply_markup=menu)
        await message.answer(text=f"Твои плейлисты: ", reply_markup=playlists)
    else:
        await message.answer(text="У вас нет плейлистов")


@dp.message_handler(lambda m: m.text == "Удалить плейлист")
async def delete_playlist(message: types.Message):
    playlists = InlineKeyboardMarkup()
    cur.execute(f"SELECT name, playlist_id FROM playlists WHERE user_id = {message.from_user.id}")
    data = [x for x in cur]
    if data:
        for i in data:
            playlists.add(InlineKeyboardButton(text=i[0], callback_data=f"delete playlist:{i[-1]}"))
        await message.answer(text="Выбери плейлист", reply_markup=menu)
        await message.answer(text=f"Твои плейлисты: ", reply_markup=playlists)
    else:
        await message.answer("У вас нет плейлистов")


@dp.message_handler(Text(equals="Отмена", ignore_case=True), state=["*"])
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text="Возврат в меню", reply_markup=menu)


@dp.message_handler(state=Create.name)
async def name_playlist(message: types.Message, state: FSMContext):
    await state.update_data(name=f"{message.text}")
    data = await state.get_data()
    if data.get("name", False):
        cur.execute(f"INSERT INTO playlists(user_id, name) VALUES ({message.from_user.id}, \'{data.get('name')}\')")
        conn.commit()
        await state.finish()
        await message.answer("Плейлист создан", reply_markup=menu)
    else:
        await message.answer("Что-то пошло не так, попробуй ещё раз")


@dp.callback_query_handler(lambda c: c.data.startswith("delete playlist:"))
async def delete_the_playlist(callback: types.CallbackQuery):
    playlist_id = callback.data.replace("delete playlist:", "")
    cur.execute(f"DELETE FROM playlists WHERE playlist_id = {playlist_id}")
    conn.commit()
    await callback.answer("Плейлист удалён")


@dp.callback_query_handler(lambda c: c.data.startswith("playlist_id:"))
async def open_playlist_handler(callback: types.CallbackQuery):
    open_playlist = InlineKeyboardMarkup()
    await callback.answer(text="Успешно")
    playlist_id = callback.data.replace("playlist_id:", "")
    cur.execute(f"SELECT name FROM playlists WHERE playlist_id = {playlist_id}")
    name_of_playlist = [x for x in cur]
    cur.execute(f"SELECT link, link_id FROM links WHERE playlist_id = {playlist_id}")
    data = [x for x in cur]
    if data:
        open_playlist.add(InlineKeyboardButton(text="Отправить всё", callback_data=f"all playlist:{playlist_id}"))
        for i in data:
            open_playlist.add(InlineKeyboardButton(text=f"{YouTube(i[0]).author} {YouTube(i[0]).title}",
                                                   callback_data=f"link to:{i[0]}"))
        open_playlist.add(InlineKeyboardButton(text="Очистить плейлист", callback_data=f"clear playlist:{playlist_id}"))
        await callback.message.edit_text(text=f"{name_of_playlist[0][0]}")
        await callback.message.edit_reply_markup(reply_markup=open_playlist)
    else:
        await callback.message.answer("Плейлист пуст")


@dp.callback_query_handler(lambda c: c.data.startswith("all playlist:"))
async def send_all_playlist(callback: types.CallbackQuery):
    delete_music = InlineKeyboardMarkup()
    playlist_id = callback.data.replace("all playlist:", "")
    cur.execute(f"SELECT link FROM links WHERE playlist_id = {playlist_id}")
    data = [x for x in cur]
    if data:
        for i in data:
            path = download_from_utube(i[0])
            with open(path, "rb") as audio:
                delete_music.add(InlineKeyboardButton(text="Удалить из плейлиста",
                                                      callback_data=f"delete music:{i[0]}"))
                await callback.answer(text="Успешно")
                await bot.send_audio(callback.from_user.id, audio, reply_markup=delete_music)
                os.remove(path)
    else:
        await callback.message.edit_text("Плейлист пуст")


@dp.callback_query_handler(lambda c: c.data.startswith("delete music:"))
async def delete_from_playlist(callback: types.CallbackQuery):
    link = callback.data.replace("delete music:", "")
    cur.execute(f"DELETE FROM links WHERE link = '{link}'")
    conn.commit()
    await callback.message.delete_reply_markup()


@dp.callback_query_handler(lambda c: c.data.startswith("link to:"))
async def download_playlist(callback: types.CallbackQuery):
    await callback.answer("Успешно")
    delete_music = InlineKeyboardMarkup()
    link = callback.data.replace("link to:", "")
    path = download_from_utube(link)
    try:
        with open(path, "rb") as audio:
            delete_music.add(InlineKeyboardButton(text="Удалить из плейлиста",
                                                  callback_data=f"delete music:{link}"))
            await callback.answer(text="Успешно")
            await bot.send_audio(callback.from_user.id, audio, reply_markup=delete_music)
            os.remove(path)
    except TypeError:
        await bot.send_message(chat_id=callback.from_user.id, text="Данный запрос уже не доступен")


@dp.callback_query_handler(lambda c: c.data.startswith("clear playlist:"))
async def clear_playlist(callback: types.CallbackQuery):
    playlist_id = callback.data.replace("clear playlist:", "")
    cur.execute(f"DELETE FROM links WHERE playlist_id = {playlist_id}")
    conn.commit()
    await callback.answer("Плейлист очищен")
    await callback.message.delete_reply_markup()
    await callback.message.edit_text("Плейлист очищен")


@dp.callback_query_handler(lambda c: c.data.startswith("link to playlist:"))
async def link_handler(callback: types.CallbackQuery):
    choice_the_playlist = InlineKeyboardMarkup()
    cur.execute(f"SELECT name, playlist_id FROM playlists WHERE user_id = {callback.from_user.id}")
    data = [x for x in cur]
    if not data:
        await callback.answer("Плейлистов не найдено")
        return None
    link = callback.data.replace("link to playlist:", "")
    for i in data:
        choice_the_playlist.add(InlineKeyboardButton(text=f"{i[0]}",
                                                     callback_data=f"id_link:{i[-1]},{link}"))
    await callback.message.edit_reply_markup(reply_markup=choice_the_playlist)


@dp.callback_query_handler(lambda c: c.data.startswith("id_link:"))
async def add_music_to_playlist(callback: types.CallbackQuery):
    data = callback.data.replace("id_link:", "").split(",")
    await callback.message.delete_reply_markup()
    cur.execute(f"INSERT INTO links(playlist_id, link) VALUES ({data[0]}, '{data[-1]}')")
    conn.commit()
    await callback.answer(text="Песня добавлена")
