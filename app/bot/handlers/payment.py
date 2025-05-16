from aiogram import Router, F
from aiogram.types import Message
from app.bot.templates.responses import send_payment_link
import logging
from app.core.config import get_settings
from app.core.bot_instance import get_bot

logger = logging.getLogger(__name__)
router = Router()
settings = get_settings()

async def send_payment_reminder_message(chat_id: int):
    """Відправка нагадування про оплату"""
    try:
        bot = get_bot()
        message = await bot.send_message(
            chat_id=chat_id,
            text="Ви намагалися оплатити послугу, але оплату не було завершено. Спробуйте ще раз."
        )

        await send_payment_link(message.chat.id, message.from_user.id)
    except Exception as e:
        logger.error(f"Помилка при відправці нагадування: {str(e)}")

async def process_payment(chat_id: int):
    """Відправка нагадування про оплату"""
    try:
        bot = get_bot()
        message = await bot.send_message(
            chat_id=chat_id,
            text="Дякую за оплату!"
        )
        await message.answer("Тепер ви маєте доступ до наступного відео.")

        await message.answer_video(
            video=settings.HYPOTHYROIDISM_VIDEO_FILE_ID,
            caption="Ось ваше наступне відео про гіпотиреоз.",
            protect_content=True,
        )
    except Exception as e:
        logger.error(f"Помилка при відправці відео після оплати: {str(e)}")

@router.message(F.text == "Оплата")
async def hard_payment(message: Message):
    """Обробка натискання на кнопку оплати"""
    try:
        # Відправляємо нове повідомлення
        await send_payment_link(message.from_user.id, message.chat.id)

    except Exception as e:
        logger.error(f"Помилка при обробці платежу: {str(e)}")
        await message.answer("Помилка при обробці платежу", show_alert=True)

@router.message(F.text == "Контент")
async def hard_content(message: Message):
    """Обробка натискання на кнопку оплати"""
    try:
        # Відправляємо нове повідомлення
        await process_payment(message.from_user.id)

    except Exception as e:
        logger.error(f"Помилка при обробці платежу: {str(e)}")
        await message.answer("Помилка при обробці платежу", show_alert=True)



