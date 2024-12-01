import requests
import logging
from utils.regular_func import get_country
from data_base import sqlite_db
from typing import List, Dict
from config_data.config import headers
from telebot.types import InputMediaPhoto

logger = logging.getLogger('app.utils.hotels_api')


def api_request(url: str, querystring: Dict) -> Dict:
    """
    Функция отправки запроса к API
    :param url: url запроса
    :param querystring: параметр запроса в формате словаря
    """
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=15)
        if response.status_code == 200:
            logger.debug('response OK')
            result = response.json()
        else:
            result = None
    except requests.exceptions.Timeout as e:
        logger.exception(e)
        result = None
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        result = None

    return result


def find_city(user_id: int, city: str, locale: str) -> str | bool | None:
    """Функция отправляющая запрос для поиска города"""
    querystring = {"query": city, "locale": locale, "currency": "USD"}
    result = api_request("https://hotels4.p.rapidapi.com/locations/v2/search", querystring)
    if result is None:
        return None
    city_info = result['suggestions'][0]['entities']
    all_city = []
    for city_var in city_info:
        if city_var['type'] == 'CITY':
            country_info = city_var['caption']
            country_name = get_country(country_info)
            city_final = (city_var['name'], country_name, city_var['destinationId'])
            all_city.append(city_final)
    if len(all_city) > 1:  # по запросу найдено несколько вариантов (например поиск Paris)
        city_text = 'По вашему запросу найдены следующие варианты:\n'
        count = 0
        for var_city in all_city:
            count += 1
            sqlite_db.add_city(user_id, count, var_city[2], var_city[0], var_city[1])
            city_text += f'{count}. {var_city[1]}\n'
        city_text += 'Для продолжения поиска введите номер нужного варианта.'
        sqlite_db.add_info(user_id, 'current_session', 'variant_city', count)
        return city_text
    elif len(all_city) == 1:
        sqlite_db.add_info(user_id, 'current_session', 'destination_ID', all_city[0][2])
        sqlite_db.add_info(user_id, 'current_session', 'city_name', all_city[0][0])
        sqlite_db.add_info(user_id, 'current_session', 'country_name', all_city[0][1])
        return True
    else:
        return False


def list_hotels(querystring: dict) -> List[Dict]:
    """Получает список содержащий информацию об отелях, полученных в результате поиска"""
    response_json = api_request('https://hotels4.p.rapidapi.com/properties/list', querystring)
    if response_json is None:
        return []
    result = response_json['data']['body']['searchResults']['results']
    return result


def hotel_photo(id_hotel: str, num_photo: int):
    """Функция формирующая список ссылок на фото для заданного отеля"""
    querystring = {"id": id_hotel}
    response_json = api_request("https://hotels4.p.rapidapi.com/properties/get-hotel-photos", querystring)
    if response_json is None:
        return None
    links = []
    for photo in range(num_photo):
        link = response_json['hotelImages'][photo]['baseUrl']
        link_size = link.format(size='w')
        links_media = InputMediaPhoto(media=link_size)
        links.append(links_media)
    return links
