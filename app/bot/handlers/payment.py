from aiogram import Router, F
from aiogram.types import Message
from app.bot.templates.responses import send_payment_link
import logging
from app.core.config import get_settings
from app.core.bot_instance import get_bot
from app.bot.texts.replies import BotReplies
from app.bot.keyboards.content import get_content_inline_keyboard

logger = logging.getLogger(__name__)
router = Router()
settings = get_settings()

async def send_payment_reminder_message(chat_id: int):
    """Відправка нагадування про оплату"""
    try:
        bot = get_bot()
        message = await bot.send_message(
            chat_id=chat_id,
            text=BotReplies.PAYMENT_REMINDER
        )

        await send_payment_link(message.chat.id, message.from_user.id)
    except Exception as e:
        logger.error(f"Error send payment reminder: {str(e)}")

async def process_payment(chat_id: int):
    """Відправка платного контенту"""
    try:
        bot = get_bot()
        message = await bot.send_message(
            chat_id=chat_id,
            text=BotReplies.PAYMENT_SUCCESS
        )
        await message.answer(BotReplies.AFTER_PAYMENT_MESSAGE)

        await message.answer(
                "📚 Виберіть контент, який вас цікавить:",
                reply_markup=get_content_inline_keyboard()
            )

    except Exception as e:
        logger.error(f"Error send video after payment: {str(e)}")

@router.message(F.text == "Оплата")
async def hard_payment(message: Message):
    """Обробка натискання на кнопку оплати"""
    try:
        # Відправляємо нове повідомлення
        await send_payment_link(message.from_user.id, message.chat.id)

    except Exception as e:
        logger.error(f"Error payment process: {str(e)}")
        await message.answer("Помилка при обробці платежу", show_alert=True )

@router.message(F.text == "Контент")
async def hard_content(message: Message):
    """Обробка натискання на кнопку оплати"""
    try:
        # Відправляємо нове повідомлення
        await process_payment(message.from_user.id)

    except Exception as e:
        logger.error(f"Error payment process: {str(e)}")
        await message.answer("Помилка при обробці платежу", show_alert=True)

