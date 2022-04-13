from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    [[KeyboardButton(text="Плейлисты")]], resize_keyboard=True
)

my_or_create = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    KeyboardButton(text="Создать плейлист"),
    KeyboardButton(text="Удалить плейлист")).add(
    KeyboardButton(text="Мои плейлисты")).add(
    KeyboardButton(text="Отмена")
)

join_to_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text="Отмена"))
