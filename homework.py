import logging
from logging import StreamHandler
import os
import sys
import time

import requests

import telegram

from dotenv import load_dotenv

from exceptions import (
    EnvironmentParameterError, RequestStatusCodeError, RequestError,
    ResponseKeyError, HomeworkKeyError, StatusHomeworkError, ResponseJsonError
)

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


def init_logger() -> logging.Logger:
    """Создаёт и настраивает логер."""
    handler = StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)
    logger.addHandler(handler)
    return logger


def check_tokens() -> None:
    """Проверяет наличие переменных окружения."""
    environment_variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }

    for key, value in environment_variables.items():
        if not value:
            logger.critical(
                "Отсутствует обязательная переменная окружения: "
                f"'{key}'. Программа принудительно остановлена."
            )

            raise EnvironmentParameterError(
                f"Отсутствует обязательная переменная окружения: '{key}'. "
                "Программа принудительно остановлена."
            )


def send_message(bot: telegram.bot.Bot, message: str) -> None:
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Бот отправил сообщение "{message}"')
    except Exception as error:
        logger.error(f'При отправке сообщения выдало ошибку "{error}"')


def get_api_answer(timestamp: int) -> dict:
    """Делает запрос к эндпоинту и проверяет его корректность."""
    payload = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        logger.error('Сбой в работе программы: '
                     'При запросе к API '
                     f'произошла ошибка {error}.')
        raise RequestError('При запросе к API '
                           f'произошла ошибка {error}.')

    if response.status_code != 200:
        logger.error(
            f'Сбой в работе программы: Эндпоинт {ENDPOINT}. '
            f'Код ответа API: {response.status_code}'
        )
        raise RequestStatusCodeError(
            f'Эндпоинт {ENDPOINT}. Код ответа API: {response.status_code}'
        )

    try:
        return response.json()
    except Exception:
        logger.error(
            'Сбой в работе программы: Данные в response '
            'не соответсвуют формату JSON.'
        )
        raise ResponseJsonError(
            'Данные в response не соответсвуют формату JSON.'
        )


def check_response(response: dict) -> list:
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        logger.error(
            "Сбой в работе программы: "
            "Получены данные "
            "'response' не в виде словаря."
        )
        raise TypeError("Полученные данные "
                        "'response' не в виде словаря.")

    if 'homeworks' not in response:
        logger.error("Сбой в работе программы: "
                     "Отсутвует ожидаемый ключ 'homeworks'.")
        raise ResponseKeyError("Отсутвует ожидаемый ключ 'homeworks'.")

    if not response['homeworks']:
        logger.debug('Новый статус домашней работы отсутсвует.')

    if not isinstance(response['homeworks'], list):
        logger.error(
            "Сбой в работе программы: "
            "Получены данные под ключом "
            "'homeworks' не в виде списка."
        )
        raise TypeError("Полученные данные под ключом "
                        "'homeworks' не в виде списка.")

    return response['homeworks']


def parse_status(homework: dict) -> str:
    """Извлекает информацию о конкретной домашней работе."""
    if 'homework_name' not in homework:
        logger.error(
            "Сбой в работе программы: "
            "Отсутвует ожидаемый ключ 'homework_name'."
        )
        raise HomeworkKeyError("Отсутвует ожидаемый ключ 'homework_name'.")

    if 'status' not in homework:
        logger.error(
            "Сбой в работе программы: "
            "Отсутвует ожидаемый ключ 'status'."
        )
        raise HomeworkKeyError("Отсутвует ожидаемый ключ 'status'.")

    if homework['status'] not in HOMEWORK_VERDICTS:
        logger.error(
            "Сбой в работе программы: Неожиданный статус домашней работы. "
            f"status: '{homework['status']}'."
        )
        raise StatusHomeworkError("Неожиданный статус домашней работы. "
                                  f"status: '{homework['status']}'.")

    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[homework['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
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


logger = init_logger()
if __name__ == '__main__':
    main()
