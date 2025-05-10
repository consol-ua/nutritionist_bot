class BotException(Exception):
    """Базовий клас для всіх винятків бота"""
    pass


class DatabaseError(BotException):
    """Помилки бази даних"""
    pass


class ValidationError(BotException):
    """Помилки валідації даних"""
    pass


class APIError(BotException):
    """Помилки API"""
    pass


class SchedulerError(BotException):
    """Помилки планувальника завдань"""
    pass 