# handlers.py
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from datetime import datetime
from utils import get_sheet, user_exists

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "Привіт! Це базовий бот який вносить данні в google sheet"
    
    await update.message.reply_text(welcome_message)

    """
    Обробляє команду /start.  Якщо користувач вже в базі, вітає його,
    інакше пропонує надіслати номер телефону.
    """
    user = update.effective_user

    sheet = get_sheet()

    if user_exists(sheet, user.id):
        await update.message.reply_text("👋 Ти вже в системі 😊", reply_markup=ReplyKeyboardRemove()) #Прибираємо клавіатуру
    else:
        # Кнопка для надсилання номера телефону
        button = KeyboardButton("📱 Надіслати номер", request_contact=True)
        keyboard = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Щоб зареєструватись, надішли, будь ласка, свій номер телефону:",
            reply_markup=keyboard
        )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє отриманий контактний номер телефону.
    Додає користувача до таблиці, якщо його там ще немає, та вітає його.
    """
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
            await update.message.reply_text(f"🎉 Вітаємо, {user.first_name}! Тебе успішно додано до системи.", reply_markup=ReplyKeyboardRemove()) #Прибираємо клавіатуру після обробки та вітаємо
        else:
            await update.message.reply_text("Ти вже зареєстрований 😊", reply_markup=ReplyKeyboardRemove()) #Прибираємо клавіатуру
    else:
        await update.message.reply_text("⚠️ Можна надсилати тільки свій контакт.")