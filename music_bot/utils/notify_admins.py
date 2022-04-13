import logging

from aiogram import Dispatcher


from data.config import ADMINS


async def on_startup_notify(dp: Dispatcher, users: list = None):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Запуск")
        except Exception as err:
            logging.exception(err)
    if users is not None:
        for user in users:
            try:
                await dp.bot.send_message(int(user[0]), "Напишите /start для коректной работы бота")
            except Exception as err:
                logging.exception(err)
