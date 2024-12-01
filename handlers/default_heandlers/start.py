from loader import bot
from telebot.types import Message
from data_base import sqlite_db


@bot.message_handler(commands=['start'])
def send_welcome(message: Message) -> None:
    """
    Функция приветствует пользователя, а также проверяет есть ли он в базе данных.
    Если пользователь отсутствует в базе данных, создается запись о нем в базе.
    Если пользователь присутствует в базе данных, выдается сообщение о продолжении работы.
    """

    if sqlite_db.check_user(message.from_user.id) is True:
        # logger.info(f'Пользователь {message.from_user.username} ({message.from_user.id}) ввёл команду {message.text}')
        bot.send_message(message.chat.id, 'Привет, я готов к работе. '
                                          'Для получения информации и возможностях бота введите команду /help.')
        sqlite_db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name,
                           message.from_user.last_name)
    else:
        bot.send_message(message.chat.id, 'Привет, продолжаем работу. '
                                          'Для получения информации и возможностях бота введите команду /help')
