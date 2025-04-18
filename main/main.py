import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import start, contact_handler
from flask import Flask, request, jsonify
import threading


# # ⬇️ Завантажує змінні з .env (тільки локально, не потрібне в продакшені)
# dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
# load_dotenv(dotenv_path)

# 🔧 Змінні середовища
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"  # 📌 Telegram буде слати POST запити сюди

# 📦 Flask App і Telegram Application
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# 📩 Обробники
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.CONTACT, contact_handler))

# 🧠 Обробка Telegram-оновлень
async def process_update(update):
    print(f"▶️ В process_update()")
    await application.process_update(update)
    print("✅ Завершено process_update()")

# 📌 Event loop для стабільного async виконання в Cloud Run
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def process_update_in_thread(update):
    """Обробка оновлення в окремому потоці."""
    loop.run_until_complete(process_update(update))

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    """Отримує оновлення від Telegram через вебхук."""
    try:
        data = request.get_json()
        print(f"Отримано оновлення: {data}")
        update = Update.de_json(data, application.bot)

        # 🧠 Ключовий момент: обробка в окремому потоці
        threading.Thread(target=process_update_in_thread, args=(update,)).start()

    except Exception as e:
        print(f"Помилка обробки вебхука: {e}")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"})

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

# 🚀 Локальний запуск або запуск у Cloud Run
if __name__ == "__main__":
    # 📌 Обов’язково ініціалізувати Telegram Application
    loop.run_until_complete(application.initialize())

    # ✅ Flask запускається на всіх інтерфейсах, порт задається змінною PORT
    app.run(host="0.0.0.0", port=PORT)
