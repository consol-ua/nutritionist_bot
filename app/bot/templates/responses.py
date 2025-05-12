from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.config import get_settings
from app.bot.keyboards.phone import get_phone_keyboard, remove_keyboard

settings = get_settings()

async def send_welcome_video(message: Message):
    """Відправляє відео привітання"""
    await message.answer_video(
        video=settings.START_VIDEO_FILE_ID
    )

async def send_hypothyroidism_video(message: Message):
    """Відправляє відео про гіпотиреоз та кнопку оплати"""
    # Відправляємо відео
    await message.answer_video(
        video=settings.HYPOTHYROIDISM_VIDEO_FILE_ID
    )
    
    # Відправляємо повідомлення з кнопкою
    await send_payment_link(message)

async def send_welcome_message(message: Message):
    """Відправляє привітальне повідомлення з інформацією про нутриціолога"""
    await message.answer(
        "Вітаю, на звʼязку *Світлана Марчик*\n\n"
        "✅ Дипломований практикуючий *нутриціолог*\n"
        "✅ Амбасадор Лондонського коледжу натуропатичної медицини (CNM)\n"
        "✅ Health Coach (Європейська Асоціація Коучінга / European Coaching Association — ECA)\n"
        "✅ Член Асоціації фахівців освітньої функціональної медицини (АСОФМ)\n"
        "✅ Допомогла понад 500 людям стати здоровішими та щасливішими\n"
        "✅ За моєю авторською методикою жінки стрункішають *без зривів*, при цьому харчуються смачно, різноманітно та корисно!\n",
        reply_markup=remove_keyboard(),
        parse_mode="Markdown"
    )

async def survey_message(message: Message):
    """Відправляє повідомлення з кнопкою для проходження тесту"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пройти тест", callback_data="start_survey")]
        ]
    )

    await message.answer(
        "Будь ласка, пройдіть коротке опитування для визначення поточного стану здоров'я:",
        reply_markup=keyboard
    )

async def send_registration_request(message: Message):
    """Відправляє запит на реєстрацію з кнопкою для номера телефону"""
    await message.answer(
        "Вітаю! Для реєстрації, будь ласка, натисніть кнопку нижче щоб надіслати свій номер телефону.",
        reply_markup=get_phone_keyboard()
    )

async def send_error_message(message: Message):
    """Відправляє повідомлення про помилку"""
    await message.answer(
        "❌ Виникла помилка. Спробуйте пізніше."
    )

async def send_database_error(message: Message):
    """Відправляє повідомлення про помилку бази даних"""
    await message.answer(
        "❌ Виникла помилка при збереженні даних. Спробуйте пізніше.",
        reply_markup=remove_keyboard()
    )

async def send_instagram_invite(message: Message):
    """Відправляє повідомлення з кнопкою для переходу в Instagram"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📲 Перейти в Instagram ✨",
                url="https://www.instagram.com/nutritionist_svitlana_marchyk"
            )]
        ]
    )
    
    await message.answer(
        "🎉 Вітаю! Схоже, все добре, але щоб на 100% у цьому впевнитися 👌🏻, у мене для тебе є гарна пропозиція 💌\n"
        "✍🏻 Напиши мені в дірект слово bot 🤖 — і отримай безкоштовну діагностичну консультацію 🩺✨",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def send_only_instagram_invite(message: Message):
    """Відправляє повідомлення з кнопкою для переходу в Instagram"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📲 Перейти в Instagram ✨",
                url="https://www.instagram.com/nutritionist_svitlana_marchyk"
            )]
        ]
    )
    
    await message.answer(
        "Контакт для зв'язку:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def send_payment_link(message: Message):
    """Відправляє посилання на оплату"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="💳 Оплатити консультацію",
                callback_data="payment"
            )]
        ]
    )
    
    await message.answer(
        "Для отримання детальної консультації та плану лікування, натисніть кнопку нижче:",
        reply_markup=keyboard
    ) 



