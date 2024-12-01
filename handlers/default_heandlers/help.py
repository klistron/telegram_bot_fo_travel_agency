from loader import bot
from telebot.types import Message
from keyboards.reply import menu


@bot.message_handler(commands=['help'])
def get_help(message: Message) -> None:
    """ Функция выводит текст с описанием команд бота. """
    text = 'C помощью бота Вы можете получить следующую информацию:\n' \
        '1. Узнать топ самых дешёвых отелей в городе (команда /lowprice).\n' \
        '2. Узнать топ самых дорогих отелей в городе (команда /highprice).\n' \
        '3. Узнать топ отелей, наиболее подходящих по цене и расположению от центра' \
        '(самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).\n' \
        '4. Узнать историю поиска отелей (команда /history).\n'
    bot.send_message(message.chat.id, text)
    menu.menu(message)
