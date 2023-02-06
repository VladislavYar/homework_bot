class EnvironmentParameterError(Exception):
    """Исключение при отсутсвии обязательной переменной окружения."""

    pass


class RequestStatusCodeError(Exception):
    """Исключение при статус коде отличном от 200."""

    pass


class RequestError(Exception):
    """Обработка исключения 'requests.RequestException'."""

    pass


class ResponseKeyError(Exception):
    """Исключение при отсутвие ожидаеммого ключа 'homeworks'."""

    pass


class HomeworkKeyError(Exception):
    """Исключение при отсутвие ожидаеммых ключей."""

    pass


class StatusHomeworkError(Exception):
    """Исключение при неожиданном статусе домашней работы."""

    pass
