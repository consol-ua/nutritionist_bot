from aiogram import Router
from .handlers.common import router as common_router
from app.bot.handlers.start import router as start_router

# Створюємо головний роутер
main_router = Router()

# Підключаємо всі роутери
main_router.include_router(common_router)
main_router.include_router(start_router)

def setup_routers() -> Router:
    """Налаштування всіх роутерів бота"""
    return main_router 