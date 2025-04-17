# bot.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import start, contact_handler
from flask import Flask, request, jsonify
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
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
    # Не запускайте вебхук через python-telegram-bot, Flask сам обробляє запити
    print(f"Вебсервер Flask запущено на порту {os.environ.get('PORT', 8080)}, шлях вебхука: {WEBHOOK_PATH}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))