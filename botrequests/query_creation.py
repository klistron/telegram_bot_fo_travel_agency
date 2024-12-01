from data_base import sqlite_db
from typing import Dict


def query(user_id: int) -> Dict:
    """Функция для формирования поискового запроса для команды highprice"""
    querystring = {
        "destinationId": sqlite_db.get_info('destination_ID', 'current_session', 'user_id', user_id)[0],
        "pageNumber": "1",
        "pageSize": sqlite_db.get_info('pageSize', 'current_session', 'user_id', user_id)[0],
        "checkIn": sqlite_db.get_info('checkIn', 'current_session', 'user_id', user_id)[0],
        "checkOut": sqlite_db.get_info('checkOut', 'current_session', 'user_id', user_id)[0],
        "adults1": str(sqlite_db.get_info('adults1', 'current_session', 'user_id', user_id)[0]),
        "locale": "ru_RU",
        "currency": "USD"
    }
    if isinstance(sqlite_db.get_info('children1', 'current_session', 'user_id', user_id)[0], str):
        querystring.update({"children1": sqlite_db.get_info('children1', 'current_session', 'user_id', user_id)[0]})
    if sqlite_db.get_info('commands', 'current_session', 'user_id', user_id)[0] == '/highprice':
        querystring.update({"sortOrder": "PRICE_HIGHEST_FIRST"})
    if sqlite_db.get_info('commands', 'current_session', 'user_id', user_id)[0] == '/lowprice':
        querystring.update({"sortOrder": "PRICE"})
    if sqlite_db.get_info('commands', 'current_session', 'user_id', user_id)[0] == '/bestdeal':
        querystring.update({"priceMin": str(sqlite_db.get_info('min_price', 'current_session', 'user_id', user_id)[0]),
                            "priceMax": str(sqlite_db.get_info('max_price', 'current_session', 'user_id', user_id)[0]),
                            "sortOrder": "DISTANCE_FROM_LANDMARK",
                            "landmarkIds": "Центр города"})
    # print(querystring)
    return querystring
