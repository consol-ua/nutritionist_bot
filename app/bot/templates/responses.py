from aiogram.types import Message
from app.core.config import get_settings
from app.bot.keyboards.phone import get_phone_keyboard, remove_keyboard

settings = get_settings()

async def send_welcome_video(message: Message):
    """Відправляє відео привітання"""
    await message.answer_video(
        video=settings.START_VIDEO_FILE_ID
    )

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