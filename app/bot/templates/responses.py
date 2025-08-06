from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.config import get_settings
from app.bot.keyboards.phone import get_phone_keyboard, remove_keyboard
from app.bot.templates.send_payment_link import send_payment_link
from app.bot.texts.replies import BotReplies
from app.bot.texts.buttons import BotButtons
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

async def send_welcome_video(message: Message):
    """Відправляє відео привітання"""
    try:
        await message.answer_video(
            video=settings.START_VIDEO_FILE_ID,
            protect_content=True
        )
    except Exception as e:
        logger.error(f"Error sending welcome video: {e}")
        await message.answer("🎥 Відео тимчасово недоступне")

async def send_welcome_certificate(message: Message):
    """Відправляє сертифікат привітання"""
    try:
        await message.answer_photo(
            photo=settings.START_CERTIFICAT_ID,
            protect_content=True
        )
    except Exception as e:
        logger.error(f"Error sending welcome certificate: {e}")
        await message.answer("📄 Сертифікат тимчасово недоступний")

async def send_welcome_message(message: Message):
    """Відправляє привітальне повідомлення з інформацією про нутриціолога"""
    await message.answer(BotReplies.WELCOME_MESSAGE,
        reply_markup=remove_keyboard(),
        parse_mode="Markdown"
    )

    await send_payment_link(message.chat.id, message.from_user.id)

async def send_about_message(message: Message):
    await message.answer(BotReplies.ABOUT_MESSAGE,
        reply_markup=remove_keyboard(),
        parse_mode="Markdown"
    )

async def send_registration_request(message: Message):
    """Відправляє запит на реєстрацію з кнопкою для номера телефону"""
    await message.answer(
        BotReplies.REGISTRATION_REQUEST,
        reply_markup=get_phone_keyboard()
    )

async def send_error_message(message: Message):
    """Відправляє повідомлення про помилку"""
    await message.answer(
        BotReplies.ERROR_MESSAGE,
    )

async def send_database_error(message: Message):
    """Відправляє повідомлення про помилку бази даних"""
    await message.answer(
        BotReplies.DATABASE_ERROR,
        reply_markup=remove_keyboard()
    )

async def send_instagram_invite(message: Message):
    """Відправляє повідомлення з кнопкою для переходу в Instagram"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=BotButtons.INSTAGRAM_BUTTON_TEXT,
                url=BotButtons.INSTAGRAM_URL
            )]
        ]
    )
    
    await message.answer(
        BotReplies.INSTAGRAM_INVITE,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def send_only_instagram_invite(message: Message):
    """Відправляє повідомлення з кнопкою для переходу в Instagram"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=BotButtons.INSTAGRAM_BUTTON_TEXT,
                url=BotButtons.INSTAGRAM_URL
            )]
        ]
    )
    
    await message.answer(
        BotReplies.ONLY_INSTAGRAM_INVITE,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )





