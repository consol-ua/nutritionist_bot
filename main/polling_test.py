# polling_test.py

import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ Команда /start отримана")
    await update.message.reply_text("Привіт! Бот працює!")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_polling()
