import os
import gspread
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CRED = os.getenv("GOOGLE_SHEETS_CRED")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(GOOGLE_CRED, scopes=scope)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

def user_exists(sheet, user_id):
    records = sheet.get_all_records()
    return any(str(row.get("User ID")) == str(user_id) for row in records)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    sheet = get_sheet()

    if user_exists(sheet, user.id):
        await update.message.reply_text("👋 Привіт ще раз! Ти вже в системі 😊")
    else:
        # Кнопка для надсилання номера телефону
        button = KeyboardButton("📱 Надіслати номер", request_contact=True)
        keyboard = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Привіт! Щоб зареєструватись, надішли, будь ласка, свій номер телефону:",
            reply_markup=keyboard
        )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact

    if contact and contact.user_id == user.id:
        phone = contact.phone_number
        sheet = get_sheet()

        if not user_exists(sheet, user.id):
            row = [
                user.first_name or "",
                user.last_name or "",
                f"@{user.username}" if user.username else "",
                user.id,
                phone,
                datetime.now().strftime("%Y-%m-%d")
            ]
            sheet.append_row(row)
            await update.message.reply_text("✅ Дякую! Тебе додано в таблицю.")
        else:
            await update.message.reply_text("Ти вже зареєстрований 😊")
    else:
        await update.message.reply_text("⚠️ Можна надсилати тільки свій контакт.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    print("Бот працює. Очікує контакти...")
    app.run_polling()

if __name__ == "__main__":
    main()
