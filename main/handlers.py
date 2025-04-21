# handlers.py
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
from database import db
from sheets_export import export_users_to_sheet
from dotenv import load_dotenv
import os


load_dotenv()

# Стани для ConversationHandler
WAITING_FOR_SHEET_URL = 1

# Отримуємо ідентифікатор відео з env
VIDEO_FILE_ID = os.getenv('VIDEO_FILE_ID')

async def showWelcomeMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "👋 Це бот для ведення дієти та харчування"
    
    await update.message.reply_text(welcome_message)
    
    # Відправляємо відео тільки якщо є VIDEO_FILE_ID
    if VIDEO_FILE_ID:
        try:
            await update.message.reply_video(video=VIDEO_FILE_ID, caption="Подивіться це відео, щоб дізнатись більше про наш сервіс")
            # Додаємо кнопку для опитування після відео
            survey_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Пройти опитування", callback_data="start_survey")]
            ])
            await update.message.reply_text("Будь ласка, пройдіть коротке опитування:", reply_markup=survey_keyboard)
        except Exception as e:
            await update.message.reply_text("На жаль, не вдалося надіслати відео. Спробуйте пізніше.")
    

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, command_data: str = None):
    """Обробник для кнопок меню та команд"""
    if command_data:
        # Якщо це команда
        message = update.message
        if command_data == "personal_cabinet":
            keyboard = [
                [InlineKeyboardButton("🔵 Гіпотиреоз", callback_data="hypothyroidism")],
                [InlineKeyboardButton("🟣 Інсулінорезистентність", callback_data="insulin_resistance")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ]
            await message.reply_text("👤 Особистий кабінет", reply_markup=InlineKeyboardMarkup(keyboard))
        elif command_data == "contact_menu":
            keyboard = [
                [InlineKeyboardButton("📱 Telegram", callback_data="telegram_contact")],
                [InlineKeyboardButton("📸 Instagram", callback_data="instagram_contact")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ]
            await message.reply_text("📱 Зв'язок зі мною", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Якщо це callback від кнопки
    query = update.callback_query
    await query.answer()
    
    # Якщо це відповідь на опитування
    if query.data == "start_survey":
        await start_survey(update, context)
        return
    elif query.data.startswith("survey_"):
        await handle_survey_response(update, context)
        return
    
    if query.data == "personal_cabinet":
        keyboard = [
            [InlineKeyboardButton("🔵 Гіпотиреоз", callback_data="hypothyroidism")],
            [InlineKeyboardButton("🟣 Інсулінорезистентність", callback_data="insulin_resistance")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ]
        await query.edit_message_text("👤 Особистий кабінет", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "contact_menu":
        keyboard = [
            [InlineKeyboardButton("📱 Telegram", callback_data="telegram_contact")],
            [InlineKeyboardButton("📸 Instagram", callback_data="instagram_contact")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ]
        await query.edit_message_text("📱 Зв'язок зі мною", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "hypothyroidism":
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data="personal_cabinet")]
        ]
        await query.edit_message_text("🔵 Гіпотиреоз\n\n🔜 Ця функція буде доступна незабаром!", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "insulin_resistance":
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data="personal_cabinet")]
        ]
        await query.edit_message_text("🟣 Інсулінорезистентність\n\n🔜 Ця функція буде доступна незабаром!", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "telegram_contact":
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data="contact_menu")]
        ]
        await query.edit_message_text("📱 Мій Telegram: @myTelegramAccount", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "instagram_contact":
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data="contact_menu")]
        ]
        text = "📸 Мій Instagram: [nutritionist_svitlana_marchyk](https://www.instagram.com/nutritionist_svitlana_marchyk)"
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif query.data == "export":
        await export_users(update, context)
        
    elif query.data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("👤 Особистий кабінет", callback_data="personal_cabinet")],
            [InlineKeyboardButton("📱 Зв'язок зі мною", callback_data="contact_menu")],
            [InlineKeyboardButton("📊 Експортувати користувачів", callback_data="export")]
        ]
        await query.edit_message_text("Головне меню:", reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє команду /start.  Якщо користувач вже в базі, вітає його,
    інакше пропонує надіслати номер телефону.
    """
    user = update.effective_user

    if db.user_exists(user.id):
        # Створюємо головне меню
        keyboard = [
            [KeyboardButton("👤 Особистий кабінет")],
            [KeyboardButton("📱 Зв'язок зі мною")],
            [KeyboardButton("📊 Експортувати користувачів")]
        ]
        await update.message.reply_text("Головне меню:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
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
                        
            # Видаляємо клавіатуру після успішного додавання
            await update.message.reply_text("✅ Реєстрація успішна!", reply_markup=ReplyKeyboardRemove())

            await showWelcomeMessage(update, context)
        else:
            await update.message.reply_text("Ти вже зареєстрований 😊", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("⚠️ Можна надсилати тільки свій контакт.")

async def export_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запитує посилання на таблицю для експорту"""
    if update.callback_query:
        await update.callback_query.message.reply_text("🔗 Будь ласка, надішліть посилання на Google Sheets таблицю, куди потрібно експортувати дані:")
    else:
        await update.message.reply_text("🔗 Будь ласка, надішліть посилання на Google Sheets таблицю, куди потрібно експортувати дані:")
    return WAITING_FOR_SHEET_URL

async def handle_sheet_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє отримане посилання на таблицю та виконує експорт"""
    sheet_url = update.message.text
    
    try:
        result = export_users_to_sheet(sheet_url)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при експорті: {str(e)}")
    
    return ConversationHandler.END

# Додаємо обробник текстових повідомлень
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для текстових повідомлень з панелі швидкого доступу"""
    text = update.message.text
    
    if text == "👤 Особистий кабінет":
        keyboard = [
            [InlineKeyboardButton("🔵 Гіпотиреоз", callback_data="hypothyroidism")],
            [InlineKeyboardButton("🟣 Інсулінорезистентність", callback_data="insulin_resistance")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ]
        await update.message.reply_text("👤 Особистий кабінет", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif text == "📱 Зв'язок зі мною":
        keyboard = [
            [InlineKeyboardButton("📱 Telegram", callback_data="telegram_contact")],
            [InlineKeyboardButton("📸 Instagram", callback_data="instagram_contact")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ]
        await update.message.reply_text("📱 Зв'язок зі мною", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif text == "📊 Експортувати користувачів":
        await export_users(update, context)

async def start_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Початок опитування"""
    query = update.callback_query
    await query.answer()
    
    # Питання 1
    keyboard = [
        [InlineKeyboardButton("Так", callback_data="survey_q1_yes")],
        [InlineKeyboardButton("Ні", callback_data="survey_q1_no")]
    ]
    await query.edit_message_text(
        "Питання 1/3:\nЧи є у вас проблеми зі щитовидною залозою?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_survey_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка відповідей опитування"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("survey_q1"):
        # Зберігаємо відповідь на перше питання
        context.user_data['q1'] = "Так" if data.endswith("yes") else "Ні"
        
        # Питання 2
        keyboard = [
            [InlineKeyboardButton("Так", callback_data="survey_q2_yes")],
            [InlineKeyboardButton("Ні", callback_data="survey_q2_no")]
        ]
        await query.edit_message_text(
            "Питання 2/3:\nЧи є у вас проблеми з вагою?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("survey_q2"):
        # Зберігаємо відповідь на друге питання
        context.user_data['q2'] = "Так" if data.endswith("yes") else "Ні"
        
        # Питання 3
        keyboard = [
            [InlineKeyboardButton("Так", callback_data="survey_q3_yes")],
            [InlineKeyboardButton("Ні", callback_data="survey_q3_no")]
        ]
        await query.edit_message_text(
            "Питання 3/3:\nЧи дотримувались ви раніше дієти?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("survey_q3"):
        # Зберігаємо відповідь на третє питання
        context.user_data['q3'] = "Так" if data.endswith("yes") else "Ні"
        
        # Показуємо результати і головне меню
        results = (
            "✅ Дякуємо за відповіді!\n\n"
            f"1. Проблеми зі щитовидною залозою: {context.user_data['q1']}\n"
            f"2. Проблеми з вагою: {context.user_data['q2']}\n"
            f"3. Досвід дотримання дієти: {context.user_data['q3']}"
        )
        
        # Зберігаємо результати в базу даних або відправляємо адміністратору
        
        # Показуємо головне меню
        keyboard = [
            [InlineKeyboardButton("👤 Особистий кабінет", callback_data="personal_cabinet")],
            [InlineKeyboardButton("📱 Зв'язок зі мною", callback_data="contact_menu")],
            [InlineKeyboardButton("📊 Експортувати користувачів", callback_data="export")]
        ]
        await query.edit_message_text(f"{results}\n\nГоловне меню:", reply_markup=InlineKeyboardMarkup(keyboard))