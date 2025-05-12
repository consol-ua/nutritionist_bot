from aiogram import Router
from app.bot.handlers import start, common, survey, payment, menu

# Створюємо головний роутер
main_router = Router()

# Включаємо роутери
main_router.include_router(start.router)
main_router.include_router(common.router)
main_router.include_router(survey.router)
main_router.include_router(payment.router)
main_router.include_router(menu.router) 

def setup_routers() -> Router:
    """Налаштування всіх роутерів бота"""
    return main_router 