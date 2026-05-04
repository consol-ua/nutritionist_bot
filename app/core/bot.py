from app.core.bot_instance import bot, dp, get_bot, get_dispatcher

# Імпортуємо роутери після створення бота
from app.bot.routers import main_router

# Додаємо роутер
dp.include_router(main_router)