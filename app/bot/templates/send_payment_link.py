from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.config import get_settings
from app.services.monobank_service import MonobankService, MonobankPayment
from app.db.firestore import firestore_client
import logging
from app.core.bot_instance import get_bot

logger = logging.getLogger(__name__)
settings = get_settings()
bot = get_bot()

async def send_payment_link(user_id: int, chat_id: int):
    """Відправляє посилання на оплату"""
    try:
        # Створюємо сервіс Monobank
        monobank_service = MonobankService(api_token=settings.MONOBANK_API_TOKEN)
        
        # Створюємо URL для повернення до бота
        bot_username = settings.BOT_USERNAME
        redirect_url = f"https://t.me/{bot_username}"
        webhook_url=f"{settings.MONOBANK_WEBHOOK_URL}/{user_id}"
        
        # Створюємо платіж
        payment = MonobankPayment(
            amount=10000,  # 100 грн (в копійках)
            redirect_url=redirect_url,
            webhook_url=webhook_url
        )
        
        # Створюємо платіж і отримуємо URL
        payment_data = await monobank_service.create_payment(payment)
        payment_url = payment_data.get("pageUrl")
        payment_invoice_id = payment_data.get("invoiceId")

        await firestore_client.save_payment(user_id, payment_invoice_id, "initialized")
        
        # Створюємо кнопку з посиланням на оплату
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="💳 Оплатити",
                    url=payment_url,
                )]
            ]
        )

        await bot.send_message(
                chat_id=user_id,
                text="Щоб перейти до наступних відео, тисни оплатити:",
                reply_markup=keyboard              
            )
        
    except Exception as e:
        logger.error(f"Помилка при створенні платежу: {str(e)}")
        await bot.send_message(
            chat_id=user_id,
            text="Виникла помилка при створенні платежу. Будь ласка, спробуйте пізніше."
        ) 