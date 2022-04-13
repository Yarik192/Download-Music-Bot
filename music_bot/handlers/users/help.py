from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Запуск бота",
            "/help - Получить справку\n"
            "По всем вопросам писать - https://t.me/nonlocal_192")
    
    await message.answer("\n".join(text))
