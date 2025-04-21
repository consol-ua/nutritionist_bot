import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, BotCommand, BotCommandScopeDefault
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from handlers import start, contact_handler, export_users, handle_sheet_url, WAITING_FOR_SHEET_URL, button_callback, handle_text_message
from flask import Flask, request, jsonify
import threading
from database import db

# Завантажуємо змінні середовища
load_dotenv()

# Змінні середовища
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"

# Flask App і Telegram Application
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Налаштування команд меню
async def setup_commands():
    commands = [
        BotCommand("start", "🏠 Головне меню"),
        BotCommand("cabinet", "👤 Особистий кабінет"),
        BotCommand("contact", "📱 Зв'язок зі мною"),
        BotCommand("export", "📊 Експортувати користувачів")
    ]
    
    # Видаляємо старі команди
    await application.bot.delete_my_commands()
    
    # Встановлюємо команди для всіх чатів
    await application.bot.set_my_commands(
        commands,
        scope=BotCommandScopeDefault()
    )

# Обробники
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("cabinet", lambda update, context: button_callback(update, context, "personal_cabinet")))
application.add_handler(CommandHandler("contact", lambda update, context: button_callback(update, context, "contact_menu")))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("export", export_users)],
    states={
        WAITING_FOR_SHEET_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sheet_url)]
    },
    fallbacks=[]
))
application.add_handler(MessageHandler(filters.CONTACT, contact_handler))

# Додаємо обробник текстових повідомлень (має бути останнім)
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

# Обробка Telegram-оновлень
async def process_update(update):
    print(f"▶️ В process_update()")
    await application.process_update(update)
    print("✅ Завершено process_update()")

# Event loop для стабільного async виконання в Cloud Run
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

        # Обробка в окремому потоці
        threading.Thread(target=process_update_in_thread, args=(update,)).start()

    except Exception as e:
        print(f"Помилка обробки вебхука: {e}")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"})

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

# Локальний запуск або запуск у Cloud Run
if __name__ == "__main__":
    # Ініціалізуємо Telegram Application
    loop.run_until_complete(application.initialize())
    
    # Налаштовуємо команди меню
    loop.run_until_complete(setup_commands())

    # Flask запускається на всіх інтерфейсах
    app.run(host="0.0.0.0", port=PORT)
