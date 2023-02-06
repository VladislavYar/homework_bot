import logging
from logging import StreamHandler
import os
import sys
import time

import requests

from telegram import Bot

from dotenv import load_dotenv

from exceptions import (
    EnvironmentParameterError, RequestParameterError,
    ResponseKeyError, HomeworkKeyError, StatusHomeworkError
)

handler = StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
logger.addHandler(handler)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет наличие переменных окружения."""
    environment_variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    if None in environment_variables.values():
        none_variable = (
            list(environment_variables.keys())
            [list(environment_variables.values()).index(None)]
        )
        logger.critical("Отсутствует обязательная переменная окружения: "
                        f"'{none_variable}'. "
                        "Программа принудительно остановлена.")

        raise EnvironmentParameterError("Отсутствует обязательная "
                                        "переменная окружения: "
                                        f"'{none_variable}'. "
                                        "Программа принудительно остановлена.")


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Бот отправил сообщение "{message}"')
    except Exception as error:
        logger.error(f'При отправке сообщения выдало ошибку "{error}"')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту и проверяет его корректность."""
    payload = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    status_code = response.status_code

    if status_code == 400 or status_code == 401:
        parameter_by_status_сode = {'400': 'from_date', '401': 'Authorization'}
        logger.error(
            "Сбой в работе программы: "
            "Некорректное значение параметра "
            f"{parameter_by_status_сode[str(status_code)]}. "
            f"Код ответа API: {status_code}"
        )
        raise RequestParameterError(
            "Некорректное значение параметра "
            f"{parameter_by_status_сode[str(status_code)]}. "
            f"Код ответа API: {status_code}"
        )
    elif status_code == 404:
        logger.error(
            "Сбой в работе программы: "
            "Эндпоинт https://practicum.yandex.ru/api/"
            "user_api/homework_statuses/ недоступен. "
            "Код ответа API: 404"
        )
        raise RequestParameterError(
            "Эндпоинт https://practicum.yandex.ru/api/"
            "user_api/homework_statuses/ недоступен. "
            "Код ответа API: 404"
        )
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not response['homeworks']:
        logger.debug('Новый статус домашней работы отсутсвует.')
    elif 'homeworks' not in response:
        logger.error(
            "Сбой в работе программы: "
            "Отсутвует ожидаемый ключ 'homeworks'."
        )
        raise ResponseKeyError("Отсутвует ожидаемый ключ 'homeworks'.")

    return response['homeworks']


def parse_status(homework):
    """Извлекает информацию о конкретной домашней работе."""
    if 'homework_name' not in homework:
        logger.error(
            "Сбой в работе программы: "
            "Отсутвует ожидаемый ключ 'homework_name'."
        )
        raise HomeworkKeyError("Отсутвует ожидаемый ключ 'homework_name'.")
    elif 'status' not in homework:
        logger.error(
            "Сбой в работе программы: "
            "Отсутвует ожидаемый ключ 'status'."
        )
        raise HomeworkKeyError("Отсутвует ожидаемый ключ 'status'.")
    elif homework['status'] not in HOMEWORK_VERDICTS:
        logger.error(
            "Сбой в работе программы: Неожиданный статус домашней работы. "
            f"status: '{homework['status']}'."
        )
        raise StatusHomeworkError("Неожиданный статус домашней работы. "
                                  f"status: '{homework['status']}'.")

    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[homework['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = Bot(token=TELEGRAM_TOKEN)

    timestamp = int(time.time())

    old_error_message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)

            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != old_error_message:
                send_message(bot, message)
                old_error_message = message

        timestamp = int(time.time())
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
