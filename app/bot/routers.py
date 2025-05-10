from aiogram import Router
from .handlers.common import router as common_router

# Створюємо головний роутер
main_router = Router()

# Підключаємо всі роутери
main_router.include_router(common_router)

def setup_routers() -> Router:
    """Налаштування всіх роутерів бота"""
    return main_router 