from fastapi import APIRouter, Request, HTTPException
from aiogram.types import Update
from ...core.bot import bot, dp
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    try:
        update_dict = await request.json()
        logger.info(f"Отримано вебхук: {update_dict}")
        
        # Створюємо об'єкт Update з валідацією
        update = Update.model_validate(update_dict)
        
        # Використовуємо правильний метод для aiogram 3.x
        await dp.feed_update(update)
        
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Помилка обробки вебхука: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


