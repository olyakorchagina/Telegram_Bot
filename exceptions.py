class MissingVariableException(Exception):
    """Исключение при отсутствии хотя бы одной переменной окружения."""

    pass


class GetApiAnswerException(Exception):
    """Исключение при сбое запроса к API."""

    pass


class MissingKeyException(Exception):
    """Исключение при отсутствии ожидаемых ключей в ответе API."""

    pass


class UndocumentException(Exception):
    """Исключение для недокументированного статуса домашней работы."""

    pass
