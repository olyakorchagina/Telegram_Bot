import os
import time
from pprint import pprint

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
token = os.getenv('TELEGRAM_TOKEN')
URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

bot = Bot(token=token)

timestamp = int(time.time())
params = {'from_date': timestamp}
response = requests.get(URL, headers=HEADERS, params=params).json()

pprint(response)
#pprint(type(response.get('homeworks')))


"""first_element = response.get('homeworks')[0]
homework_name = first_element.get('homework_name')
pprint(homework_name)
homework_status = first_element.get('status')
pprint(homework_status)"""

"""if homework_status == 'approved':
    print(HOMEWORK_STATUSES['approved'])"""
