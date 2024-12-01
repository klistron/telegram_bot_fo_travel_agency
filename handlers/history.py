import time
from loader import bot
from telebot.types import Message
from keyboards.reply import menu
from data_base import sqlite_db


def history_user(message: Message) -> None:
    """ Функция для вывода истории работы пользователя. """
    history_res = sqlite_db.get_history(message.from_user.id)
    if len(history_res) == 0:
        bot.send_message(message.from_user.id, 'Вы ещё не вводили команд.')
    else:
        for res in history_res:
            bot.send_message(message.from_user.id, res[0], parse_mode='HTML', disable_web_page_preview=True)
            time.sleep(2)
    menu.menu(message)
