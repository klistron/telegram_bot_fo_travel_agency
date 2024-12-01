import sqlite3
import functools
import logging
from datetime import datetime, date, timedelta
from typing import Callable, Any

logger = logging.getLogger("app.data_base.sqlite_db")


def sqlite_write(func: Callable) -> Callable:
    """ Декоратор для функций записывающих информацию в БД """
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs) -> Any:
        with sqlite3.connect('data_base/data.db', check_same_thread=False) as base:
            cur = base.cursor()
            result = func(*args, base, cur, **kwargs)
        return result
    return wrapped_func


def sqlite_read(func: Callable) -> Callable:
    """ Декоратор для функций читающих информацию в БД """
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs) -> Any:
        with sqlite3.connect('data_base/data.db', check_same_thread=False) as base:
            cur = base.cursor()
            result = func(*args, cur, **kwargs)
        return result
    return wrapped_func


def sql_start() -> None:
    """
    Функция создает подключение к базе данных, а при ее отсутствии создает её.
    Также при необходимости создаются необходимые таблицы.
    """
    base = sqlite3.connect('data_base/data.db', check_same_thread=False)
    if base:
        logger.debug('Data base OK')
    base.execute(
        'CREATE TABLE IF NOT EXISTS users(user_id INT PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT, '
        'date DATE)')
    base.commit()
    base.execute(
        'CREATE TABLE IF NOT EXISTS current_session(user_id INT PRIMARY KEY, commands TEXT, destination_ID TEXT, '
        'pageSize TEXT, checkIn DATE, checkOut DATE, locale TEXT, variant_city INT, date DATE, distance INT,'
        'adults1 INT, children1 TEXT, min_price INT, max_price INT, photo INT, city_name TXT, country_name TXT)')
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS history(user_id INT, result TEXT)')
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS cities(user_id INT, num_city INT, destinationId INT, '
                 'city_name TXT, country_name TXT)')
    base.commit()
    base.close()


@sqlite_write
def add_user(user_id: int, username: str, first_name: str, last_name: str, base: Any, cur: Any) -> None:
    """
    Функция добавляет нового пользователя в базу данных.
    """
    cur.execute('INSERT INTO users VALUES(?, ?, ?, ?, ?)',
                (user_id, username, first_name, last_name, datetime.now().date()))
    base.commit()
    cur.execute('INSERT INTO current_session VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (user_id, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                 None, None))
    base.commit()


@sqlite_read
def check_user(user_id: int, cur: Any) -> bool:
    """ Функция проверяет наличие пользователя в базе данных. """
    check = cur.execute('SELECT * FROM users WHERE user_id == ?', (user_id, ))
    if check.fetchone() is None:
        return True


@sqlite_read
def get_history(user_id: int, cur: Any) -> list:
    """ Функция выводящая историю работы пользователя. """
    history_user = cur.execute('SELECT result FROM history WHERE user_id == ?', (user_id, )).fetchall()
    return history_user


@sqlite_write
def add_history(user_id: int, history_info: str, base: Any, cur: Any) -> None:
    cur.execute('INSERT INTO history VALUES(?, ?)', (user_id, history_info))
    base.commit()


@sqlite_write
def add_info(user_id: int, name_table: str, name_val: str, value, base: Any, cur: Any) -> None:
    """Функция добавляющая информацию в заданную таблицу"""
    session_update = f'UPDATE {name_table} SET {name_val} = ? WHERE user_id = ?'
    data = (value, user_id)
    cur.execute(session_update, data)
    base.commit()


@sqlite_write
def clear_session(user_id: int, base: Any, cur: Any) -> None:
    """Функция очищающая всю информацию о предыдущем запросе пользователя"""
    cur.execute('UPDATE current_session SET commands = ?, destination_ID = ?, pageSize = ?, checkIn = ?,'
                'checkOut = ?, locale = ?, variant_city = ?, date = ?, adults1 = ?, children1 = ?,'
                ' photo = ?, city_name = ?, country_name = ?, distance = ?, min_price = ?,'
                'max_price = ? WHERE user_id = ?',
                (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                 user_id))
    base.commit()


@sqlite_read
def get_info(column: str, table: str, key, user_id, cur: Any) -> tuple:
    """Функция предоставляющая информацию из заданной таблицы"""
    session_select = f'SELECT {column} FROM {table} WHERE {key} = ?'
    required_info = cur.execute(session_select, (user_id, )).fetchone()
    return required_info


@sqlite_write
def add_city(user_id: int, num_city: int, destinationid: int, city_name: str, country_name: str,
             base: Any, cur: Any) -> None:
    """Функция добавляющая все варианты городов для временного хранения"""
    cur.execute('INSERT INTO cities VALUES(?, ?, ?, ?, ?)',
                (user_id, num_city, destinationid, city_name, country_name))
    base.commit()


@sqlite_write
def get_dest_id(number_var: int, user_id: int, base: Any, cur: Any) -> None:
    """Функция добавляющая id города в текущую сессию пользователя и очищающая таблицу
    хранящую варианты городов"""
    dest_id = cur.execute('SELECT destinationID FROM cities WHERE user_id = ? AND num_city = ?',
                          (user_id, number_var)).fetchone()
    city_name = cur.execute('SELECT city_name FROM cities WHERE user_id = ? AND num_city = ?',
                            (user_id, number_var)).fetchone()
    country_name = cur.execute('SELECT country_name FROM cities WHERE user_id = ? AND num_city = ?',
                               (user_id, number_var)).fetchone()
    add_info(user_id, 'current_session', 'destination_ID', dest_id[0])
    add_info(user_id, 'current_session', 'city_name', city_name[0])
    add_info(user_id, 'current_session', 'country_name', country_name[0])
    cur.execute('DELETE FROM cities WHERE user_id = ?', (user_id, ))
    base.commit()


@sqlite_read
def get_check_date(user_id: int, cur: Any) -> tuple:
    """Функция для определения минимальной даты, которая будет дана для выбора в календаре"""
    check_date = cur.execute('SELECT checkIn FROM current_session WHERE user_id = ?',
                             (user_id, )).fetchone()
    if check_date[0] is None:
        check_date = date.today()
        return check_date, 'checkIn'
    else:
        check_date = datetime.strptime(check_date[0], '%Y-%m-%d') + timedelta(days=1)
        return check_date.date(), 'checkOut'
