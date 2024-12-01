import re
from data_base import sqlite_db


def check_lang(city_name: str) -> str:
    """Функция для определения на каком языке введено название города"""
    result = re.match(r'[а-яА-ЯёЁ]', city_name)
    if result is None:
        return 'en_US'
    else:
        return 'ru_RU'


def get_country(text: str) -> str:
    """Функция для получения названия страны (региона)"""
    flag = False
    while flag is False:
        if re.search(r'<', text) is None:
            flag = True
        else:
            ind_st = text.index('<')
            ind_fin = text.index('>')
            text = text[:ind_st] + text[ind_fin + 1:]
    return text


def format_age(data_age: str, user_id: int) -> bool:
    """Функция форматирующая введенные возраст детей и проверяющая корректность ввода"""
    del_tab = re.sub(r'\s+', '', data_age, flags=re.UNICODE)
    if re.search(r'[^0-9,]', del_tab):
        return False
    else:
        check_age = del_tab.split(',')
        for age in check_age:
            if int(age) > 17:
                return False
        sqlite_db.add_info(user_id, 'current_session', 'children1', del_tab)
        return True


def format_distance(data_dist: str) -> float:
    """Функция конвертирующая полученное значение дистанции в действительное число"""
    repl_comma = re.sub(r',', '.', data_dist, flags=re.UNICODE)
    only_num = re.sub(r'\s\D+', '', repl_comma, flags=re.UNICODE)
    return float(only_num)


def format_price(price: str) -> int:
    only_digit = re.sub(r',', '', price, flags=re.UNICODE)
    digit_price = int(only_digit)
    return digit_price
