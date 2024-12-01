import telebot
from typing import Any
from loader import bot


def menu(message: Any) -> None:
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    itembtn1 = telebot.types.KeyboardButton('/lowprice')
    itembtn2 = telebot.types.KeyboardButton('/highprice')
    itembtn3 = telebot.types.KeyboardButton('/bestdeal')
    itembtn4 = telebot.types.KeyboardButton('/history')
    itembtn5 = telebot.types.KeyboardButton('/help')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
    bot.send_message(message.from_user.id, 'Выберите команду:', reply_markup=markup)
