import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (GetApiAnswerException, MissingVariableException,
                        UndocumentException)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    format='%(asctime)s, %(name)s, %(levelname)s,  %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.ERROR
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info('Сообщение отправлено')
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Запрос к API Практикум.Домашка."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            logger.error(f'Ошибка. Статус ответа: {response.status_code}')
            raise GetApiAnswerException(
                f'Ошибка. Статус ответа: {response.status_code}'
            )
        logger.debug('Запрос выполнен')
    except Exception as error:
        logger.error(f'Сбой при запросе к API: {error}')
        raise GetApiAnswerException(f'Сбой при запросе к API: {error}')
    return response.json()


def check_response(response):
    """Проверка ответа от API."""
    if type(response) != dict:
        raise TypeError('Должен вернуться словарь')
    try:
        homeworks = response.get('homeworks')
        if type(homeworks) != list:
            raise TypeError('Должен вернуться список')
    except KeyError:
        logger.error('Отсутствует ожидаемый ключ словаря в ответе API')
        raise MissingKeyException(
            'Отсутствует ожидаемый ключ словаря в ответе API'
        )
    return homeworks


def parse_status(homework):
    """Проверка статуса домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None:
        logger.error('Отсутствует ожидаемый ключ словаря в ответе API')
        raise KeyError(
            'Отсутствует ожидаемый ключ словаря в ответе API'
        )
    if homework_status is None:
        logger.error('Отсутствует ожидаемый ключ словаря в ответе API')
        raise KeyError(
            'Отсутствует ожидаемый ключ словаря в ответе API'
        )

    verdict = HOMEWORK_STATUSES.get(homework_status)
    if verdict is None:
        raise UndocumentException(
            'Недокументированный статус домашней работы'
        )

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    if (PRACTICUM_TOKEN is None
            or TELEGRAM_TOKEN is None
            or TELEGRAM_CHAT_ID is None):
        logger.critical('Отсутствуют необходимые переменные окружения!')
        return False
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            logger.debug('Отправляется запрос')
            response = get_api_answer(current_timestamp)
            logger.debug('Ответ получен')
            homeworks = check_response(response)
            if len(homeworks) != 0:
                last_homework = response.get('homeworks')[0]
                message = parse_status(last_homework)
                send_message(bot, message)
                current_timestamp = response.get('current_date')
                time.sleep(RETRY_TIME)
            logger.debug('Статус не изменился')
            time.sleep(RETRY_TIME)
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
