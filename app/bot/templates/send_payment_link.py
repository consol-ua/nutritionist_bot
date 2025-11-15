from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.config import get_settings
from app.services.wayforpay_service import WayForPayService, WayForPayPayment
from app.db.firestore import firestore_client
import logging
import time
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
        
        # Створюємо сервіс WayForPay
        wayforpay_service = WayForPayService(
            merchant_account=settings.WAYFORPAY_MERCHANT_ACCOUNT,
            merchant_secret_key=settings.WAYFORPAY_MERCHANT_SECRET_KEY,
            merchant_domain_name=settings.WAYFORPAY_MERCHANT_DOMAIN_NAME
        )
        
        # Створюємо URL для повернення до бота
        service_url = f"{settings.WAYFORPAY_WEBHOOK_URL}/{user_id}"
        
        # Генеруємо унікальний order_reference
        order_reference = f"order_{user_id}_{int(time.time())}"
        
        # Створюємо платіж
        payment = WayForPayPayment(
            order_reference=order_reference,
            amount=340.00,  # 340 грн
            currency="UAH",
            product_name=["Доступ до контенту"],
            product_count=[1],
            product_price=[340.00],
            service_url=service_url
        )

        saved_payment = await firestore_client.get_payment_by_user(user_id)

        local_payment_order_reference = saved_payment.get("order_reference") if saved_payment else None

        if local_payment_order_reference:
            invoice = await wayforpay_service.check_payment_status(local_payment_order_reference)

            # Перевіряємо, чи є помилка в відповіді
            if invoice.get('error'):
                logger.warning(f"Error checking payment status: {invoice.get('error')}, creating new payment")
                payment_data = await wayforpay_service.create_payment(payment)
            # Перевіряємо статус платежу (WayForPay використовує інші статуси)
            elif invoice.get('transactionStatus') == 'Approved' or invoice.get('reasonCode') == 1100:
                payment_data = {
                    "invoiceUrl": saved_payment.get('payment_url'),
                    "orderReference": local_payment_order_reference
                }
            else:
                payment_data = await wayforpay_service.create_payment(payment)
        else:
            payment_data = await wayforpay_service.create_payment(payment)

        # Перевіряємо, чи є помилка в відповіді API
        if payment_data.get('error'):
            error_msg = payment_data.get('error', 'Unknown error')
            logger.error(f"WayForPay API error: {error_msg}, Response: {payment_data}")
            raise Exception(f"WayForPay API error: {error_msg}")
        
        # Створюємо платіж і отримуємо URL
        # WayForPay повертає invoiceUrl замість pageUrl
        payment_url = payment_data.get("invoiceUrl") or payment_data.get("pageUrl")
        payment_order_reference = payment_data.get("orderReference") or payment.order_reference
        
        if not payment_url:
            logger.error(f"No payment URL in response: {payment_data}")
            raise Exception("No payment URL received from WayForPay API")

        await firestore_client.save_payment(user_id, payment_order_reference, "initialized", payment_url)
        
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
                text=BotReplies.PAYMENT_MESSAGE,
                reply_markup=keyboard
            )
        
    except Exception as e:
        logger.error(f"Error create payment: {str(e)}")
        await bot.send_message(
            chat_id=user_id,
            text=BotReplies.PAYMENT_ERROR
        ) 

