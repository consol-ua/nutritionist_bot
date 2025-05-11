from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from app.core.config import get_settings
from app.bot.middlewares.error_handler import ErrorHandlerMiddleware
from app.bot.routers import main_router

settings = get_settings()

# Ініціалізація бота
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

def create_dispatcher() -> Dispatcher:
    """Створення диспетчера з налаштуваннями"""
    # Створюємо диспетчер з ботом
    dp = Dispatcher(bot=bot)
    
    # Додаємо middleware
    dp.update.middleware(ErrorHandlerMiddleware())
    
    # Включаємо головний роутер
    dp.include_router(main_router)
    
    return dp

# Створюємо диспетчер
dp = create_dispatcher() 