from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.bot.templates.responses import send_only_instagram_invite, send_welcome_message
from app.bot.texts.replies import BotReplies
from app.bot.keyboards.content import get_content_keyboard
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
    await send_welcome_message(message)

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
                reply_markup=get_content_keyboard()
            )
        else:
            await message.answer(
                "🔒 У вас немає доступу до цього контенту. Для отримання доступу, будь ласка, оплатіть курс."
            )
            await send_payment_link(message.chat.id, message.from_user.id)
            
    except DatabaseError as e:
        logger.error(f"Error checking user access: {e}")
        await message.answer("❌ Виникла помилка при перевірці доступу. Спробуйте пізніше.")
    except Exception as e:
        logger.error(f"Unexpected error in content handler: {e}")
        await message.answer("❌ Виникла неочікувана помилка. Спробуйте пізніше.")

@router.message(F.text.in_(["Контент 1", "Контент 2", "Контент 3"]))
async def handle_content_selection(message: Message):
    """Обробка натискання кнопок контенту"""
    content_map = {
        "Контент 1": " Це перший блок контенту. Тут може бути інформація про щитоподібну залозу.",
        "Контент 2": " Це другий блок контенту. Тут може бути інформація про харчування.",
        "Контент 3": " Це третій блок контенту. Тут може бути інформація про вітаміни та мікроелементи."
    }
    
    selected_content = content_map.get(message.text, "Контент не знайдено")
    await message.answer(selected_content) 

