import datetime
from utils import regular_func
from data_base import sqlite_db


def dist_check(hotels: list, user_id: int) -> list:
    """Функция для проверки соответствует ли расстояние от отеля требованиям пользователя"""
    target = sqlite_db.get_info('distance', 'current_session', 'user_id', user_id)[0]
    new_hotels = []
    for hotel in hotels:
        if float(target) > regular_func.format_distance(hotel['landmarks'][0]['distance']):
            new_hotels.append(hotel)
        else:
            break
    return new_hotels


def history_len(user_id: int, old_text: str, new_text: str, finish_message: str) -> str:
    """Функция проверяет длину сообщения и при приближении к порогу записывает базу данных."""
    if len(old_text) + len(new_text) < 4096:
        history_info = old_text + '\n' + new_text
    else:
        sqlite_db.add_history(user_id, old_text)
        history_info = f'Дата поиска: {datetime.date.today()}\n' \
                       f'{finish_message}\n(продолжение)\n'
    return history_info


def diff_day(user_id: int) -> int:
    """Функция для получения дней проживания"""
    check_in = sqlite_db.get_info('checkIn', 'current_session', 'user_id', user_id)[0]
    check_out = sqlite_db.get_info('checkOut', 'current_session', 'user_id', user_id)[0]
    date_in = datetime.datetime.strptime(check_in, '%Y-%m-%d')
    date_out = datetime.datetime.strptime(check_out, '%Y-%m-%d')
    period = date_out - date_in
    period_num = int(period.total_seconds()/(60 * 60 * 24))
    return period_num
