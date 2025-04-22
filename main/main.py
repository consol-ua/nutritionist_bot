import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand, BotCommandScopeDefault
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from handlers import start, contact_handler, export_users, handle_sheet_url, WAITING_FOR_SHEET_URL, button_callback, handle_text_message
from flask import Flask, request, jsonify
import threading
from database import db

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Створюємо глобальний event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Ініціалізуємо бота
loop.run_until_complete(application.initialize())
loop.run_until_complete(setup_commands())

# Функція для запуску event loop в окремому потоці
def run_event_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Запускаємо event loop в окремому потоці
threading.Thread(target=run_event_loop, daemon=True).start()

# Обробка Telegram-оновлень
async def process_update(update):
    logger.info(f"▶️ В process_update()")
    await application.process_update(update)
    logger.info("✅ Завершено process_update()")

def process_update_in_thread(update):
    """Обробка оновлення в окремому потоці."""
    asyncio.run_coroutine_threadsafe(process_update(update), loop)

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    """Отримує оновлення від Telegram через вебхук."""
    try:
        data = request.get_json()
        logger.info(f"Отримано оновлення: {data}")
        update = Update.de_json(data, application.bot)

        # Обробка в окремому потоці
        threading.Thread(target=process_update_in_thread, args=(update,)).start()

    except Exception as e:
        logger.error(f"Помилка обробки вебхука: {e}")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"})

@app.route("/ping", methods=['GET'])
def ping():
    return "pong", 200

# Flask запускається на всіх інтерфейсах
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
