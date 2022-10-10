class GetApiAnswerException(Exception):
    """Исключение при сбое запроса к API."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        print('calling str')
        if self.message:
            return 'GetApiAnswerException, {0} '.format(self.message)
        else:
            return 'GetApiAnswerException has been raised'


class UndocumentException(Exception):
    """Исключение для недокументированного статуса домашней работы."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        print('calling str')
        if self.message:
            return 'UndocumentException, {0} '.format(self.message)
        else:
            return 'UndocumentException has been raised'
