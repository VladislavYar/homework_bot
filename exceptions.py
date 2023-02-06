class EnvironmentParameterError(Exception):
    """Исключение при отсутсвии обязательной переменной окружения."""

    pass


class RequestParameterError(Exception):
    """Исключение при некорректнных параметрах запроса."""

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
