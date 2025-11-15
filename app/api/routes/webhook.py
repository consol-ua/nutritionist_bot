from fastapi import APIRouter, Request, HTTPException
from app.core.bot_instance import get_bot, get_dispatcher
from aiogram.types import Update
import logging
from app.core.config import get_settings
from app.db.firestore import firestore_client
from datetime import datetime, timedelta
from app.services.scheduler import scheduler
from apscheduler.triggers.date import DateTrigger
from app.services.wayforpay_service import WayForPayService
from app.bot.handlers.payment import send_payment_reminder_message, process_payment

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
bot = get_bot()
dp = get_dispatcher()

@router.post("/webhook")
async def webhook(request: Request):
    try:
        update_dict = await request.json()
        
        # Конвертуємо словник в об'єкт Update
        update = Update.model_validate(update_dict)
        
        # Виправлений синтаксис для aiogram 3.x
        await dp.feed_update(bot=bot, update=update)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def send_payment_reminder(chat_id: int, order_reference: str):
    """Відправка нагадування про оплату"""
    try:
        has_access = await firestore_client.user_has_access(chat_id)

        if has_access:
            return
        
        if not order_reference:
            return
        
        # WayForPay не має методу remove_payment, тому просто відправляємо нагадування
        await send_payment_reminder_message(chat_id)
        
    except Exception as e:
        logger.error(f"Error sending payment reminder: {str(e)}")

@router.post("/wayforpay/{chat_id}")
async def wayforpay_webhook(request: Request, chat_id: str):
    """Обробка вебхука від WayForPay"""

    try:
        data = await request.json()
        
        # Перевіряємо підпис вебхука
        wayforpay_service = WayForPayService(
            merchant_account=settings.WAYFORPAY_MERCHANT_ACCOUNT,
            merchant_secret_key=settings.WAYFORPAY_MERCHANT_SECRET_KEY,
            merchant_domain_name=settings.WAYFORPAY_MERCHANT_DOMAIN_NAME
        )
        
        if not wayforpay_service.verify_webhook_signature(data):
            logger.warning(f"Invalid webhook signature for chat_id: {chat_id}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Перевіряємо статус платежу
        order_reference = data.get("orderReference")
        transaction_status = data.get("transactionStatus")
        reason_code = data.get("reasonCode")
        
        if not order_reference:
            raise HTTPException(status_code=400, detail="No order reference provided")
        
        # WayForPay використовує transactionStatus та reasonCode
        # reasonCode 1100 = успішний платіж, transactionStatus = "Approved"
        if transaction_status == "Approved" or reason_code == 1100:
            await process_payment(chat_id)

            await firestore_client.save_job_id(chat_id, None)
            await firestore_client.update_payment_status(order_reference, "success")
            await firestore_client.update_user_access(chat_id)

            scheduler.remove_job(job_id=order_reference)

        # Статус "InProcessing" або "WaitingAuthComplete" означає, що платіж створено
        if transaction_status in ["InProcessing", "WaitingAuthComplete"] or reason_code == 1100:
            user = await firestore_client.get_user(chat_id)
            job_id = user.get('job_id')
            if user is None:
                logger.warning(f"User {chat_id} not found in database")
                return {"status": "ok"}
                
            if not job_id:
                await firestore_client.save_job_id(chat_id, order_reference)
                scheduler.add_job(
                    job_id=order_reference,
                    func=send_payment_reminder,
                    trigger=DateTrigger(run_date=datetime.now() + timedelta(minutes=30)),
                    args=[chat_id, order_reference]
                )
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing WayForPay webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

