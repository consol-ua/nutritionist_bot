from aiogram import Router, types
from aiogram.filters import Command
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обробник команди /start"""
    user_name = message.from_user.full_name
    await message.answer(
        f"Привіт, {user_name}! 👋\n\n"
        "Я бот-помічник для відстеження харчування. "
        "Я допоможу вам вести облік ваших прийомів їжі та аналізувати ваш раціон.\n\n"
        "Використовуйте команди:\n"
        "/help - показати список команд\n"
        "/add_meal - додати прийом їжі\n"
        "/stats - подивитися статистику"
    )
    logger.info(f"Користувач {user_name} (ID: {message.from_user.id}) запустив бота") 