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
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        logger.info(f'Отправка статуса домашки: {message}')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as error:
        raise telegram.error.TelegramError(
            f'Ошибка при отправке сообщения: {error}'
        )


def get_api_answer(current_timestamp):
    """Запрос к API Практикум.Домашка."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.debug('Отправка запроса')
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logger.debug('Запрос выполнен, ответ получен')
    except Exception as error:
        raise GetApiAnswerException(
            f'Сбой при запросе: {ENDPOINT}, {HEADERS}, {params}. {error}'
        )
    else:
        if response.status_code != HTTPStatus.OK:
            raise GetApiAnswerException(
                f'Ошибка при ответе от API: {ENDPOINT}, {HEADERS}, {params}.'
                f'Статус ответа: {response.status_code}'
            )
    return response.json()


def check_response(response):
    """Проверка ответа от API."""
    if not isinstance(response, dict):
        raise TypeError(
            f'Ожидаются данные типа dict, получен: {type(response)}'
        )
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(
            f'Ожидаются данные типа list, получен: {type(homeworks)}'
        )
    return homeworks


def parse_status(homework):
    """Проверка статуса домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None:
        raise KeyError(
            'Отсутствует ключ словаря "homework_name" в ответе API'
        )
    if homework_status is None:
        raise KeyError(
            'Отсутствует ключ словаря "status" в ответе API'
        )

    verdict = VERDICTS.get(homework_status)
    if verdict is None:
        raise UndocumentException(
            'Недокументированный статус домашней работы'
        )

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(tokens)


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют необходимые переменные окружения!')
        sys.exit('Отсутствуют необходимые переменные окружения!')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if len(homeworks) != 0:
                last_homework = response.get('homeworks')[0]
                message = parse_status(last_homework)
                send_message(bot, message)
            else:
                logger.debug('Статус не изменился')
            current_timestamp = response.get('current_date')
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
