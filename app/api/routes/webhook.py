from fastapi import APIRouter, Request, HTTPException
from app.core.bot import dp, bot
from aiogram.types import Update
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def webhook(request: Request):
    try:
        update_dict = await request.json()
        logger.info(f"отримано вебхук: {update_dict}")
        
        # Конвертуємо словник в об'єкт Update
        update = Update.model_validate(update_dict)
        
        # Виправлений синтаксис для aiogram 3.x
        await dp.feed_update(bot=bot, update=update)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Помилка обробки вебхука: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


