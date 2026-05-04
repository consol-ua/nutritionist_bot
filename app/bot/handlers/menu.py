from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.bot.templates.responses import send_only_instagram_invite, send_about_message, send_welcome_certificate
from app.bot.texts.replies import BotReplies
from app.bot.keyboards.content import get_content_inline_keyboard
from app.db.firestore import firestore_client
from app.core.exceptions import DatabaseError
from app.bot.templates.responses import send_payment_link
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("contact"))
async def handle_contact(message: Message):
    """Обробка команди /contact"""
    await send_only_instagram_invite(message)

@router.message(Command("about"))
async def handle_about(message: Message):
    """Обробка команди /about"""
    await send_welcome_certificate(message)
    await send_about_message(message)

@router.message(Command("menu"))
async def handle_menu(message: Message):
    """Обробка команди /menu"""
    await message.answer(BotReplies.MENU_MESSAGE)

@router.message(Command("content"))
async def handle_content(message: Message):
    """Обробка команди /content - показує повідомлення з кнопками контенту тільки користувачам з доступом"""
    try:
        # Перевіряємо чи має користувач доступ
        has_access = await firestore_client.user_has_access(message.from_user.id)
        
        if has_access:
            await message.answer(
                "📚 Виберіть контент, який вас цікавить:",
                reply_markup=get_content_inline_keyboard()
            )
        else:
            await message.answer(
                BotReplies.NOT_HAS_ACCESS_TO_CONTENT
            )
            await send_payment_link(message.chat.id, message.from_user.id)
            
    except DatabaseError as e:
        logger.error(f"Error checking user access: {e}")
        await message.answer(BotReplies.ERROR_MESSAGE)
    except Exception as e:
        logger.error(f"Unexpected error in content handler: {e}")
        await message.answer(BotReplies.ERROR_MESSAGE)


