import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.bot import bot, dp
from app.api.routes.webhook import router as webhook_router
from app.services.scheduler import scheduler

# Налаштування логування
logger = setup_logging()

# Отримання налаштувань
settings = get_settings()

async def setup_webhook():
    """Встановлення вебхука для бота"""
    print(f"settings.WEBHOOK_URL: {settings.WEBHOOK_URL}")
    webhook_url = f"{settings.WEBHOOK_URL}/webhook"
    await bot.set_webhook(url=webhook_url)
    logger.info(f"Вебхук встановлено: {webhook_url}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Встановлення вебхука
    await setup_webhook()
    # Запуск планувальника
    scheduler.start()
    logger.info("Додаток запущено")
    yield
    # Зупинка бота
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Додаток зупинено")

# Ініціалізація FastAPI
app = FastAPI(title="Telegram Bot API", lifespan=lifespan)

# Додавання роутерів
app.include_router(webhook_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    ) 