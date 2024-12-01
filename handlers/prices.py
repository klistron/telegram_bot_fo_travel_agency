import time
import datetime
import telebot
import logging
from botrequests import query_creation
from loader import bot
from telebot.types import Message
from keyboards.reply import menu, calendar
from data_base import sqlite_db
from utils import regular_func, hotels_api, control_func

logger = logging.getLogger("app.handlers.prices")


def command_lowprice_highprice_bestdeal(message: Message) -> None:
    """Функция для обработки команд бота"""
    sqlite_db.clear_session(message.from_user.id)  # очищает текущую сессию
    sqlite_db.add_info(message.from_user.id, 'current_session', 'date', datetime.datetime.now())
    sqlite_db.add_info(message.from_user.id, 'current_session', 'commands', message.text)
    bot.send_message(message.from_user.id, 'Введите город или страну на русском или английском языке:')
    bot.register_next_step_handler(message, get_city)


def get_city(message: Message) -> None:  # получаем город
    """Функция для обработки введенного пользователем города"""
    if message.text == '/menu':
        menu.menu(message)
    else:
        city = message.text.lower()
        locale = regular_func.check_lang(city)
        sqlite_db.add_info(message.from_user.id, 'current_session', 'locale', locale)
        city_info = hotels_api.find_city(message.from_user.id, city, locale)
        if city_info is True:
            calendars(message)
        elif city_info is False:
            bot.send_message(message.from_user.id, 'По вашему запросу ничего не найдено.'
                                                   'Проверьте правильность ввода названия города или измените язык'
                                                   ' ввода и повторите запрос.\n'
                                                   'Для возврата в меню выбора команд используйте команду /menu')
            bot.register_next_step_handler(message, get_city)
        elif city_info is None:
            bot.send_message(message.from_user.id, 'Сервис не доступен. Попробуйте позже')
            menu.menu(message)
        else:
            bot.send_message(message.from_user.id, city_info)
            bot.register_next_step_handler(message, choise_country)


def choise_country(message: Message) -> None:
    """Функция для выбора города, если поиск предлагает несколько вариантов"""
    if message.text == '/menu':
        menu.menu(message)
    elif message.text.isdigit() is True:
        control_value = sqlite_db.get_info('variant_city', 'current_session', 'user_id', message.from_user.id)
        if 0 < int(message.text) <= control_value[0]:
            sqlite_db.get_dest_id(int(message.text), message.from_user.id)
            calendars(message)
        else:
            bot.send_message(message.from_user.id, 'Ошибка при вводе числа. Введите номер нужного вам варианта.\n'
                                                   'Для возврата в меню выбора команд используйте команду /menu')
            bot.register_next_step_handler(message, choise_country)
    else:
        bot.send_message(message.from_user.id, 'Для продолжения нужно ввести число. '
                                               'Введите номер нужного вам варианта.\n'
                                               'Для возврата в меню выбора команд используйте команду /menu')
        bot.register_next_step_handler(message, choise_country)


def calendars(message: Message) -> None:
    """Функция запускающая календари для ввода дат заезда и выезда"""
    bot.send_message(message.from_user.id, 'Выберите дату заезда:')
    calendar.date_input(message)
    while sqlite_db.get_info('checkIn', 'current_session', 'user_id', message.from_user.id)[0] is None:
        time.sleep(3)
    bot.send_message(message.from_user.id, 'Выберите дату выезда:')
    calendar.date_input(message)
    while sqlite_db.get_info('checkOut', 'current_session', 'user_id', message.from_user.id)[0] is None:
        time.sleep(3)
    command = sqlite_db.get_info('commands', 'current_session', 'user_id', message.from_user.id)[0]
    if command == '/bestdeal':
        bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера в отеле (в USD):\n'
                                               'Введите только число.')
        bot.register_next_step_handler(message, min_price)
    else:
        bot.send_message(message.from_user.id, 'Введите количество отелей, которые необходимо вывести '
                                               'в результате (не более 25):')
        bot.register_next_step_handler(message, page_size_func)


def min_price(message: Message) -> None:
    """Функция для получения минимальной стоимости номера при выполнении команды bestdeal"""
    if message.text == '/menu':
        menu.menu(message)
    elif message.text.isdigit() is True:
        if 0 < int(message.text):
            sqlite_db.add_info(message.from_user.id, 'current_session', 'min_price', int(message.text))
            bot.send_message(message.from_user.id, 'Введите максимальную стоимость номера в отеле (в USD):\n'
                                                   'Введите только число.')
            bot.register_next_step_handler(message, max_price)
        else:
            bot.send_message(message.from_user.id, 'Ошибка при вводе минимальной стоимости номера. '
                                                   'Введите число больше 0.\n'
                                                   'Для возврата в меню выбора команд '
                                                   'используйте команду /menu')
            bot.register_next_step_handler(message, min_price)
    else:
        bot.send_message(message.from_user.id, 'Для продолжения необходимо ввести минимальную стоимость '
                                               'номера.\n'
                                               'Для возврата в меню выбора команд используйте команду /menu')
        bot.register_next_step_handler(message, min_price)


def max_price(message: Message) -> None:
    """Функция для получения максимальной стоимости номера при выполнении команды bestdeal"""
    if message.text == '/menu':
        menu.menu(message)
    elif message.text.isdigit() is True:
        control_value = sqlite_db.get_info('min_price', 'current_session', 'user_id', message.from_user.id)
        if control_value[0] < int(message.text):
            sqlite_db.add_info(message.from_user.id, 'current_session', 'max_price', int(message.text))
            bot.send_message(message.from_user.id, 'В километрах введите дистанцию от центра города в пределах '
                                                   'которой должен быть выполнен поиск отеля:\n'
                                                   'Введите только число.')
            bot.register_next_step_handler(message, distance)
        else:
            bot.send_message(message.from_user.id, 'Ошибка при вводе максимальной стоимости номера. '
                                                   'Введите стоимость больше, чем минимальная.\n'
                                                   'Для возврата в меню выбора команд '
                                                   'используйте команду /menu')
            bot.register_next_step_handler(message, max_price)
    else:
        bot.send_message(message.from_user.id, 'Для продолжения необходимо ввести максимальную стоимость '
                                               'номера.\n'
                                               'Для возврата в меню выбора команд используйте команду /menu')
        bot.register_next_step_handler(message, max_price)


def distance(message: Message) -> None:
    """Функция для получения дистанции от центра города при выполнении команды bestdeal"""
    if message.text == '/menu':
        menu.menu(message)
    elif message.text.isdigit() is True:
        if 0 < int(message.text):
            sqlite_db.add_info(message.from_user.id, 'current_session', 'distance', int(message.text))
            bot.send_message(message.from_user.id, 'Введите количество отелей, которые необходимо вывести '
                                                   'в результате (не более 25):')
            bot.register_next_step_handler(message, page_size_func)
        else:
            bot.send_message(message.from_user.id, 'Ошибка при вводе расстояния отеля от центра. '
                                                   'Расстояние должно быть больше 0.\n'
                                                   'Для возврата в меню выбора команд '
                                                   'используйте команду /menu')
            bot.register_next_step_handler(message, distance)
    else:
        bot.send_message(message.from_user.id, 'Для продолжения необходимо ввести расстояние отеля от центра.\n'
                                               'Для возврата в меню выбора команд используйте команду /menu')
        bot.register_next_step_handler(message, distance)


def page_size_func(message: Message) -> None:
    """Функция для получения количества вариантов отелей для поиска"""
    if message.text == '/menu':
        menu.menu(message)
    elif message.text.isdigit() is True:
        if 0 < int(message.text) <= 25:
            sqlite_db.add_info(message.from_user.id, 'current_session', 'pageSize', int(message.text))
            bot.send_message(message.from_user.id, 'Сколько взрослых будет жить в номере?')
            bot.register_next_step_handler(message, number_of_adults)
        else:
            bot.send_message(message.from_user.id, 'Ошибка при вводе числа. Введите число от 1 до 25.\n'
                                                   'Для возврата в меню выбора команд '
                                                   'используйте команду /menu')
            bot.register_next_step_handler(message, page_size_func)
    else:
        bot.send_message(message.from_user.id, 'Для продолжения необходимо ввести число от 1 до 25.\n'
                                               'Для возврата в меню выбора команд используйте команду /menu')
        bot.register_next_step_handler(message, page_size_func)


def number_of_adults(message: Message) -> None:
    """Функция для получения количества взрослых, проживающих в одном номере"""
    if message.text.isdigit() is True:
        num_adults = int(message.text)
        if 0 < num_adults < 10:
            sqlite_db.add_info(message.from_user.id, 'current_session', 'adults1', num_adults)
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            itembtn1 = telebot.types.KeyboardButton('Да')
            itembtn2 = telebot.types.KeyboardButton('Нет')
            markup.add(itembtn1, itembtn2)
            bot.send_message(message.from_user.id, 'В номере будут жить дети?', reply_markup=markup)
            bot.register_next_step_handler(message, number_of_children)
        else:
            bot.send_message(message.from_user.id, 'Сколько взрослых будет жить в номере?'
                                                   ' Число взрослых гостей должно быть больше 0, '
                                                   'но меньше 10.')
            bot.register_next_step_handler(message, number_of_adults)
    else:
        bot.send_message(message.from_user.id, 'Для продолжения введите число взрослых гостей в одном номере')
        bot.register_next_step_handler(message, number_of_adults)


def number_of_children(message: Message) -> None:
    """Функция для определения будут ли в номере жить дети"""
    if message.text.lower() == 'да':
        bot.send_message(message.from_user.id, 'Введите через запятую возраст детей '
                                               '(например 5, 11):')
        bot.register_next_step_handler(message, check_child)
    elif message.text.lower() == 'нет':
        get_photo(message)
    else:
        bot.send_message(message.from_user.id, 'Для продолжения ответьте да или нет.')
        bot.register_next_step_handler(message, number_of_children)


def check_child(message: Message) -> None:
    """Функция для получения возраста детей"""
    check_age = regular_func.format_age(message.text, message.from_user.id)
    if check_age is True:
        get_photo(message)
    else:
        bot.send_message(message.from_user.id, 'Неправильно введен возраст детей или возраст ребенка превышает 17 лет! '
                                               'Пример ввода возраста детей: 5,11')
        bot.register_next_step_handler(message, check_child)


def get_photo(message: Message) -> None:
    """Функция для определения необходим ли вывод фотографий отеля"""
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    itembtn1 = telebot.types.KeyboardButton('Да')
    itembtn2 = telebot.types.KeyboardButton('Нет')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.from_user.id, 'Вывести фото отелей?', reply_markup=markup)
    bot.register_next_step_handler(message, number_of_photo)


def number_of_photo(message: Message) -> None:
    """Функция для определения сколько фотографий нужно вывести"""
    if message.text.lower() == 'да':
        bot.send_message(message.from_user.id, 'Введите количество фотографий для отеля (не более 25):')
        bot.register_next_step_handler(message, check_num_photo)
    elif message.text.lower() == 'нет':
        final(message)
    else:
        bot.send_message(message.from_user.id, 'Для продолжения ответьте да или нет.')
        bot.register_next_step_handler(message, number_of_photo)


def check_num_photo(message: Message) -> None:
    """Функция для получения количества фотографий отеля"""
    if message.text.isdigit() is True:
        num_photo = int(message.text)
        if 0 < num_photo <= 25:
            sqlite_db.add_info(message.from_user.id, 'current_session', 'photo', num_photo)
            final(message)
        else:
            bot.send_message(message.from_user.id, 'Для продолжения введите число выводимых фотографий для '
                                                   'отеля (от 1 до 25):')
            bot.register_next_step_handler(message, check_num_photo)
    else:
        bot.send_message(message.from_user.id, 'Для продолжения введите число выводимых фотографий для '
                                               'отеля (от 1 до 25):')
        bot.register_next_step_handler(message, check_num_photo)


def final(message: Message) -> None:
    """Функция осуществляющая отправку сообщений с информацией об отелях"""
    command = sqlite_db.get_info('commands', 'current_session', 'user_id', message.from_user.id)[0]
    query = query_creation.query(message.from_user.id)
    result = hotels_api.list_hotels(query)
    if isinstance(result, list) is False:
        result = []
    if command == '/bestdeal':
        result = control_func.dist_check(result, message.from_user.id)
    variants = len(result)
    finish_message = 'По вашему запросу {country} найдено вариантов: {variants}\n'.format(
        country=sqlite_db.get_info('country_name', 'current_session', 'user_id', message.from_user.id)[0],
        variants=variants
    )
    history_info = f'Дата поиска: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n' \
                   f'{finish_message}\n'
    if variants == 0:
        bot.send_message(message.from_user.id, 'Попробуйте изменить параметры запроса и выполнить новый поиск.')
    else:
        bot.send_message(message.from_user.id, finish_message)
        for hotel in result:
            try:
                info = 'Вариант {number}:\n' \
                       'Название отеля: <a href="https://www.hotels.com/ho{id}">{name}</a>\n' \
                       'Адрес отеля: {address}\n' \
                       'Расстояние от центра: {distance}\n' \
                       'Цена номера за одни сутки: {price}\n' \
                       'Стоимость за весь период проживания: ${total}\n'\
                    .format(number=result.index(hotel) + 1,
                            id=hotel['id'],
                            name=hotel['name'],
                            address=hotel['address']['streetAddress'],
                            distance=hotel['landmarks'][0]['distance'],
                            price=hotel['ratePlan']['price']['current'],
                            total=regular_func.format_price(
                                hotel['ratePlan']['price']['current'][1:]) * control_func.diff_day(
                                message.from_user.id))
                bot.send_message(message.from_user.id, info, parse_mode='HTML', disable_web_page_preview=True)
                photos = sqlite_db.get_info('photo', 'current_session', 'user_id', message.from_user.id)[0]
                history_info = control_func.history_len(user_id=message.from_user.id, old_text=history_info,
                                                        new_text=info, finish_message=finish_message)
                if isinstance(photos, int):
                    links_photo = hotels_api.hotel_photo(hotel['id'], photos)
                    if links_photo is None:
                        bot.send_message(message.from_user.id, 'Фото отсутствует.')
                    else:
                        bot.send_media_group(message.from_user.id, links_photo)
            except KeyError as e:
                logger.error(f"KeyError happened: {e}")
                error_info = 'Вариант {number}: \n' \
                             'Название отеля: <a href="https://www.hotels.com/ho{id}">{name}</a>\n'  \
                             'Отсутствует полная информация по данному отелю.\n' \
                    .format(number=result.index(hotel) + 1, name=hotel['name'], id=hotel['id'])
                bot.send_message(message.from_user.id, error_info, parse_mode='HTML', disable_web_page_preview=True)
                history_info = control_func.history_len(user_id=message.from_user.id, old_text=history_info,
                                                        new_text=error_info, finish_message=finish_message)
    sqlite_db.add_history(message.from_user.id, history_info)
    menu.menu(message)
