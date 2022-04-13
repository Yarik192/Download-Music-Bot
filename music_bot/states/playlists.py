from aiogram.dispatcher.filters.state import StatesGroup, State


class Create(StatesGroup):
    name = State()


class Playlists(StatesGroup):
    link = State()
