# main.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import start, contact_handler
from flask import Flask, request, jsonify
import asyncio

# load_dotenv() 
# тільки локально

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))
# для гугл клауд

WEBHOOK_PATH = "/webhook"  # Шлях, на який Telegram надсилатиме оновлення

app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.CONTACT, contact_handler))

async def process_update(update):
    await application.process_update(update)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    """Отримує оновлення від Telegram через вебхук."""
    try:
        data = request.get_json()
        print(f"Отримано оновлення: {data}")
        update = Update.de_json(data, application.bot)

        # 🧠 Ключовий момент: не run, а run_coroutine_threadsafe
        asyncio.run_coroutine_threadsafe(process_update(update), loop)

    except Exception as e:
        print(f"Помилка обробки вебхука: {e}")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    asyncio.run(application.initialize())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
  
