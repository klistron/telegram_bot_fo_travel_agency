from loader import bot
from telebot.types import Message
from data_base import sqlite_db


def get_text_messages(message: Message) -> None:
    """
    Функция, предлагающая ознакомиться с разделом help при получении в боте любого текстового сообщения.
    """
    bot.send_message(message.chat.id, '{0} воспользуйтесь командой /help чтобы узнать о возможностях бота.'.format(
        sqlite_db.get_info('username', 'users', 'user_id', message.from_user.id)[0]
    ))
