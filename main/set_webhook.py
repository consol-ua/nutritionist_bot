import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

async def set_webhook():
    if not BOT_TOKEN or not WEBHOOK_URL:
        print("❌ BOT_TOKEN або WEBHOOK_URL не задано у .env")
        return

    try:
        bot = Bot(token=BOT_TOKEN)
        success = await bot.set_webhook(url=WEBHOOK_URL)

        if success:
            print(f"✅ Вебхук успішно встановлено: {WEBHOOK_URL}")
        else:
            print("❌ Не вдалося встановити вебхук")

    except TelegramError as e:
        print(f"❌ Telegram API error: {e}")
    except Exception as e:
        print(f"❌ Інша помилка: {e}")

if __name__ == "__main__":
    asyncio.run(set_webhook())
