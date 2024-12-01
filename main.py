import handlers
import logging
from data_base import sqlite_db
from loader import bot
from utils.set_bot_commands import set_default_commands
from telebot.types import Message


def init_logger(name: str) -> None:
    logger = logging.getLogger(name)
    format_log = '%(asctime)s :: %(name)s:%(lineno)s :: %(levelname)s :: %(message)s'
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(filename='logs/botlog.log')
    fh.setFormatter(logging.Formatter(format_log))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.debug('logger was initialized')


init_logger("app")

sqlite_db.sql_start()  # проверяем базу данных, при необходимости создается файл и таблицы


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def prices_func(message: Message) -> None:
    handlers.prices.command_lowprice_highprice_bestdeal(message)


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    handlers.history.history_user(message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message: Message) -> None:
    handlers.any_text.get_text_messages(message)


if __name__ == "__main__":
    set_default_commands(bot)
    bot.polling(none_stop=True, interval=0)
