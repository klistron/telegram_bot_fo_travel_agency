from loader import bot
from telebot.types import Message
from typing import Any
from data_base import sqlite_db
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


@bot.message_handler(commands=['date'])
def date_input(message: Message) -> None:
    check_date = sqlite_db.get_check_date(message.from_user.id)
    calendar, step = DetailedTelegramCalendar(min_date=check_date[0], locale='ru').build()
    DetailedTelegramCalendar()
    bot.send_message(message.chat.id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c: Any) -> None:
    check_date = sqlite_db.get_check_date(c.from_user.id)
    result, key, step = DetailedTelegramCalendar(min_date=check_date[0], locale='ru').process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result and check_date[1] == 'checkIn':
        sqlite_db.add_info(c.from_user.id, 'current_session', 'checkIn', result)
        bot.edit_message_text(f"Выбранная дата заезда: {result}",
                              c.message.chat.id,
                              c.message.message_id)
    elif result and check_date[1] == 'checkOut':
        sqlite_db.add_info(c.from_user.id, 'current_session', 'checkOut', result)
        bot.edit_message_text(f"Выбранная дата выезда: {result}",
                              c.message.chat.id,
                              c.message.message_id)
