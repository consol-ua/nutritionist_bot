from fastapi import APIRouter, Request, HTTPException
from app.core.bot_instance import get_bot, get_dispatcher
from aiogram.types import Update
import logging
from app.core.config import get_settings
from app.db.firestore import firestore_client
from datetime import datetime, timedelta
from app.services.scheduler import scheduler
from apscheduler.triggers.date import DateTrigger
from app.services.monobank_service import MonobankService
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
        logger.info(f"received webhook: {update_dict}")
        
        # Конвертуємо словник в об'єкт Update
        update = Update.model_validate(update_dict)
        
        # Виправлений синтаксис для aiogram 3.x
        await dp.feed_update(bot=bot, update=update)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def send_payment_reminder(chat_id: int, invoice_id: str):
    """Відправка нагадування про оплату"""
    try:
        logger.info(f"Starting payment reminder for invoice_id: {invoice_id}")
        
        if not invoice_id:
            logger.error("Empty invoice_id received")
            return
            
        monobank_service = MonobankService(api_token=settings.MONOBANK_API_TOKEN)
        
        try:
            await monobank_service.remove_payment(invoice_id)
            logger.info(f"Successfully removed payment for invoice_id: {invoice_id}")
        except Exception as e:
            logger.error(f"Failed to remove payment: {str(e)}")
        
        # Викликаємо функцію з handlers/payment.py
        await send_payment_reminder_message(chat_id)
        
        # Оновлюємо статус в базі даних
        await firestore_client.update_payment_status(invoice_id, "expired")
        
    except Exception as e:
        logger.error(f"Error sending payment reminder: {str(e)}")
        logger.error(f"invoice_id: {invoice_id}")

@router.post("/monobank/{chat_id}")
async def monobank_webhook(request: Request, chat_id: str):
    """Обробка вебхука від Monobank"""
    logger.info(f"Monobank chat_id: {chat_id}")

    try:
        data = await request.json()
        logger.info(f"Received Monobank webhook: {data}")
        
        # Перевіряємо статус платежу
        invoice_id = data.get("invoiceId")
        status = data.get("status")
        if not invoice_id:
            raise HTTPException(status_code=400, detail="No invoice ID provided")
        
        if status == "success":
            await process_payment(chat_id)

            await firestore_client.save_job_id(chat_id, None)
            await firestore_client.update_payment_status(invoice_id, status)
            scheduler.remove_job(job_id=invoice_id)

        if status == 'created':
            user = await firestore_client.get_user(chat_id)
            job_id = user.get('job_id')
            if user is None:
                logger.warning(f"User {chat_id} not found in database")
                return {"status": "ok"}
                
            if not job_id:
                logger.info(f"Scheduling payment reminder for invoice_id: {invoice_id}")

                await firestore_client.save_job_id(chat_id, invoice_id)
                scheduler.add_job(
                    job_id=invoice_id,
                    func=send_payment_reminder,
                    trigger=DateTrigger(run_date=datetime.now() + timedelta(minutes=1)),
                    args=[chat_id, invoice_id]
                )
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing Monobank webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

