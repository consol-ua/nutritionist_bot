from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.bot.templates.responses import send_only_instagram_invite, send_welcome_message

router = Router()

@router.message(Command("contact"))
async def handle_contact(message: Message):
    """Обробка команди /contact"""
    await send_only_instagram_invite(message)

@router.message(Command("about"))
async def handle_about(message: Message):
    """Обробка команди /about"""
    await send_welcome_message(message)

@router.message(Command("menu"))
async def handle_menu(message: Message):
    """Обробка команди /menu"""
    await message.answer(
        "📌 Доступні команди:\n"
        "🏠 /start - на початок\n"
        "📱 /contact - зв'язок зі мною\n"
        "ℹ️ /about - про мене\n"
    ) 