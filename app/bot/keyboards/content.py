from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Router, F
from app.db.firestore import firestore_client
from app.bot.templates.responses import send_payment_link
from app.bot.texts.replies import BotReplies
from app.bot.templates.content_responses import send_content, send_content_bonus_1, send_content_bonus_2
import logging

logger = logging.getLogger(__name__)
router = Router()

def get_content_inline_keyboard() -> InlineKeyboardMarkup:
    """Створює inline клавіатуру з кнопками контенту"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Гіпотиреоз вступ",
                callback_data="content_1"
            )],
            [InlineKeyboardButton(
                text="Симптоми та причини гіпотиреозу", 
                callback_data="content_2"
            )],
            [InlineKeyboardButton(
                text="Лабораторна діагностика",
                callback_data="content_3"
            )],
            [InlineKeyboardButton(
                text="Ключові нутрієнти та харчова підтримка",
                callback_data="content_4"
            )],
            [InlineKeyboardButton(
                text="Стрес та недосип",
                callback_data="content_5"
            )],
            [InlineKeyboardButton(
                text="Про токсини та важкі метали",
                callback_data="content_6"
            )],
            [InlineKeyboardButton(
                text="Підсумки",
                callback_data="content_7"
            )], [
                InlineKeyboardButton(
                    text="🎁 Бонус 1",
                    callback_data="bonus_1"
                ),
                InlineKeyboardButton(
                    text="🎁 Бонус 2",
                    callback_data="bonus_2"
                )
            ]
        ]
    )
    return keyboard 

@router.callback_query(F.data.regexp(r"^content_\d+$"))
async def handle_content_callback(callback: CallbackQuery):
    """Обробка натискання inline кнопок контенту"""
    try:
        # Перевіряємо чи має користувач доступ
        has_access = await firestore_client.user_has_access(callback.from_user.id)
        
        if not has_access:
            await callback.answer( BotReplies.NOT_HAS_ACCESS_TO_CONTENT, show_alert=True)
            await send_payment_link(callback.message.chat.id, callback.from_user.id)
            return
        
        idx = int(callback.data.split("_")[1]) - 1
        await send_content(callback.message, idx)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in content callback: {e}")
        await callback.answer("❌ Помилка при отриманні контенту", show_alert=True)

@router.callback_query(F.data.regexp(r"^bonus_\d+$"))
async def handle_content_bonus_callback(callback: CallbackQuery):
    """Обробка натискання inline кнопок контенту"""
    try:
        # Перевіряємо чи має користувач доступ
        has_access = await firestore_client.user_has_access(callback.from_user.id)
        
        if not has_access:
            await callback.answer( BotReplies.NOT_HAS_ACCESS_TO_CONTENT, show_alert=True)
            await send_payment_link(callback.message.chat.id, callback.from_user.id)
            return
        
        if callback.data == "bonus_1":
            await send_content_bonus_1(callback.message)
        else:
            await send_content_bonus_2(callback.message)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in content callback: {e}")
        await callback.answer("❌ Помилка при отриманні контенту", show_alert=True)