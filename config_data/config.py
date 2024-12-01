import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

TOKEN = os.getenv('TOKEN')
RapidAPI_Host = os.getenv('RapidAPI_Host')
RapidAPI_Key = os.getenv('RapidAPI_Key')
headers = {
    "X-RapidAPI-Host": RapidAPI_Host,
    "X-RapidAPI-Key": RapidAPI_Key
}
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку")
)
