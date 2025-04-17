# bot.py
import os
from dotenv import load_dotenv
from telegram.ext import Update, ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import start, contact_handler
from flask import Flask, request, jsonify
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL вашого сервісу Cloud Run
WEBHOOK_PATH = "/webhook"  # Шлях, на який Telegram надсилатиме оновлення

app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.CONTACT, contact_handler))

async def process_update(update):
    await application.process_update(update)

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    """Отримує оновлення від Telegram через вебхук."""
    try:
        data = request.get_json()
        update = Update.de_json(data, application.bot)
        asyncio.run(process_update(update))
    except Exception as e:
        print(f"Помилка обробки вебхука: {e}")
        return jsonify({"status": "error"}), 500
    return jsonify({"status": "ok"})

async def main():
    """Запускає вебсервер Flask."""
    await application.initialize()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL + WEBHOOK_PATH
    )
    # Keep the app running
    # await application.updater.idle() # Не використовувати idle() з Flask
    print(f"Вебхук встановлено на: {WEBHOOK_URL + WEBHOOK_PATH}")

if __name__ == "__main__":
    asyncio.run(main())