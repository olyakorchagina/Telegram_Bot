import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import GetApiAnswerException, UndocumentException

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

VERDICTS = {
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
        logger.info('Отправка сообщения')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError as error:
        raise TelegramError(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Запрос к API Практикум.Домашка."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.debug('Отправка запроса')
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logger.debug('Запрос выполнен')
    except Exception as error:
        raise GetApiAnswerException(f'Сбой при запросе к API: {error}')
    else:
        if response.status_code != HTTPStatus.OK:
            raise GetApiAnswerException(
                f'Ошибка при запросе к API. Статус ответа: {response.status_code}'
            )
    return response.json()


def check_response(response):
    """Проверка ответа от API."""
    if not isinstance(response, dict):
        raise TypeError('Должен вернуться словарь')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Должен вернуться список')
    return homeworks


def parse_status(homework):
    """Проверка статуса домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if None in [homework_status, homework_name]:
        raise KeyError(
            'Отсутствует ожидаемый ключ словаря в ответе API'
        )

    verdict = VERDICTS.get(homework_status)
    if verdict is None:
        raise UndocumentException(
            'Недокументированный статус домашней работы'
        )

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    if not (PRACTICUM_TOKEN is None
            or TELEGRAM_TOKEN is None
            or TELEGRAM_CHAT_ID is None):
        return True
    logger.critical('Отсутствуют необходимые переменные окружения!')


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            logger.debug('Ответ получен')
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
        else:
            homeworks = check_response(response)
            if len(homeworks) != 0:
                last_homework = response.get('homeworks')[0]
                message = parse_status(last_homework)
                send_message(bot, message)
                current_timestamp = response.get('current_date')
            logger.debug('Статус не изменился')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
