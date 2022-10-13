class GetApiAnswerException(Exception):
    """Исключение при сбое запроса к API."""

    message = None

    def __init__(self, *args):
        if args:
            self.message = args[0]

    def __str__(self):
        if self.message:
            return 'GetApiAnswerException, {0} '.format(self.message)
        return 'GetApiAnswerException has been raised'


class UndocumentException(Exception):
    """Исключение для недокументированного статуса домашней работы."""

    message = None

    def __init__(self, *args):
        if args:
            self.message = args[0]

    def __str__(self):
        if self.message:
            return 'UndocumentException, {0} '.format(self.message)
        return 'UndocumentException has been raised'
