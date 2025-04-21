# handlers.py
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from datetime import datetime
from .database import db
from .sheets_export import export_users_to_sheet

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "Привіт! Це бот для ведення дієти та харчування"
    
    await update.message.reply_text(welcome_message)

    """
    Обробляє команду /start.  Якщо користувач вже в базі, вітає його,
    інакше пропонує надіслати номер телефону.
    """
    user = update.effective_user

    if db.user_exists(user.id):
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
        
        if not db.user_exists(user.id):
            user_data = {
                'user_id': user.id,
                'first_name': user.first_name or "",
                'last_name': user.last_name or "",
                'username': f"@{user.username}" if user.username else "",
                'phone': phone,
                'created_at': datetime.now()
            }
            db.add_user(user_data)
            await update.message.reply_text(f"🎉 Вітаємо, {user.first_name}! Тебе успішно додано до системи.", reply_markup=ReplyKeyboardRemove()) #Прибираємо клавіатуру після обробки та вітаємо
        else:
            await update.message.reply_text("Ти вже зареєстрований 😊", reply_markup=ReplyKeyboardRemove()) #Прибираємо клавіатуру
    else:
        await update.message.reply_text("⚠️ Можна надсилати тільки свій контакт.")

async def export_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Експортує користувачів в Google Sheets"""
    try:
        result = export_users_to_sheet()
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при експорті: {str(e)}")