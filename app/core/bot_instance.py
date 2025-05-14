from aiogram import Bot, Dispatcher
from app.core.config import get_settings

settings = get_settings()
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

def get_bot() -> Bot:
    """Отримання екземпляру бота"""
    return bot

def get_dispatcher() -> Dispatcher:
    """Отримання екземпляру диспетчера"""
    return dp 