from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from app.bot.templates.responses import send_payment_link
from app.services.scheduler import scheduler
from app.db.firestore import firestore_client
from apscheduler.triggers.date import DateTrigger
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = Router()

async def send_thank_you_message(message: Message):
    """Відправляє повідомлення подяки"""
    await message.answer("Дякую за оплату! 🎉")

@router.callback_query(F.data == "payment")
async def process_payment(callback: CallbackQuery):
    """Обробка натискання на кнопку оплати"""

    await callback.message.edit_text("Очікуйте, ми відправляємо вам повідомлення про оплату...")

    # Створюємо унікальний ID для завдання
    job_id = f"{callback.from_user.id}_{datetime.now().timestamp()}"
    
    # Додаємо відкладене повідомлення через 1 хвилину
    scheduler.add_job(
        job_id=job_id,
        func=send_thank_you_message,
        trigger=DateTrigger(run_date=datetime.now() + timedelta(minutes=1)),
        args=[callback.message]
    )
    
    # Зберігаємо job_id в базі даних
    await firestore_client.save_job_id(callback.from_user.id, job_id)
    
    await callback.answer() 