from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Router, F
from app.db.firestore import firestore_client
from app.bot.templates.responses import send_payment_link
from app.bot.texts.replies import BotReplies
from app.bot.templates.content_responses import send_content, send_content_bonus_1, send_content_bonus_2
from app.bot.keyboards.content import get_welcome_keyboard

import logging

logger = logging.getLogger(__name__)

router = Router()


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

texts = {
    "welcome_btn_1": BotReplies.WELCOME_MESSAGE_1,
    "welcome_btn_2": BotReplies.WELCOME_MESSAGE_2,
    "welcome_btn_3": BotReplies.WELCOME_MESSAGE_3,
}

@router.callback_query(F.data.startswith("welcome_btn_"))
async def handle_welcom_callback(callback: CallbackQuery):
    """Обробка натискання inline кнопок контенту"""

    button_id = callback.data
    new_text = texts.get(button_id, "no text")

    await callback.message.edit_text(
        new_text,
        reply_markup=get_welcome_keyboard(button_id),
        parse_mode="Markdown"
    )

    await callback.answer()