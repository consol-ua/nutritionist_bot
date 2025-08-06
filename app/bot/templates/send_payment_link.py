from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.config import get_settings
from app.services.monobank_service import MonobankService, MonobankPayment
from app.db.firestore import firestore_client
import logging
from app.core.bot_instance import get_bot
from app.bot.texts.buttons import BotButtons
from app.bot.texts.replies import BotReplies

logger = logging.getLogger(__name__)
settings = get_settings()
bot = get_bot()


async def send_payment_link(user_id: int, chat_id: int):
    """Відправляє посилання на оплату"""
    try:
        user = await firestore_client.get_user(user_id)


        if user.get('access'):
            return
        
        # Створюємо сервіс Monobank
        monobank_service = MonobankService(api_token=settings.MONOBANK_API_TOKEN)
        
        # Створюємо URL для повернення до бота
        bot_username = settings.BOT_USERNAME
        redirect_url = f"https://t.me/{bot_username}"
        webhook_url=f"{settings.MONOBANK_WEBHOOK_URL}/{user_id}"
        
        # Створюємо платіж
        payment = MonobankPayment(
            amount=34000,  # 340 грн (в копійках)
            redirect_url=redirect_url,
            webhook_url=webhook_url
        )

        saved_payment = await firestore_client.get_payment_by_user(user_id)

        logger.info(f'Check payment status {saved_payment}')

        local_payment_invoice_id = saved_payment.get("invoice_id") if saved_payment else None


        if local_payment_invoice_id:
            invoice = await monobank_service.check_payment_status(local_payment_invoice_id)
            logger.info(f'Check invoice {invoice}')

            if invoice.get('status') == 'created':
                logger.info('use saved payment')
                payment_data = {
                    "pageUrl": saved_payment.get('payment_url'),
                    "invoiceId": local_payment_invoice_id
                }
            else:
                logger.info('create new payment')
                payment_data = await monobank_service.create_payment(payment)
        else:
            logger.info('create new payment')
            payment_data = await monobank_service.create_payment(payment)

        
        # Створюємо платіж і отримуємо URL
        payment_url = payment_data.get("pageUrl")
        payment_invoice_id = payment_data.get("invoiceId")

        logger.info(f"invoiceId: {payment_invoice_id}")

        await firestore_client.save_payment(user_id, payment_invoice_id, "initialized", payment_url)
        
        # Створюємо кнопку з посиланням на оплату
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=BotButtons.PAYMENT_BUTTON_TEXT,
                    url=payment_url
                )]
            ]
        )

        await bot.send_message(
                chat_id=user_id,
                text=BotReplies.PAYMENT_DESCRIPTION,
                reply_markup=keyboard
            )
        
    except Exception as e:
        logger.error(f"Error create payment: {str(e)}")
        await bot.send_message(
            chat_id=user_id,
            text=BotReplies.PAYMENT_ERROR
        ) 

