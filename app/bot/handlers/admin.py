from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from app.db.firestore import firestore_client
from app.core.exceptions import DatabaseError
from app.core.config import get_settings
from app.bot.texts.replies import BotReplies
import logging

logger = logging.getLogger(__name__)
router = Router()
settings = get_settings()

@router.message(Command("grant_access"))
async def cmd_grant_access(message: Message, bot: Bot):
    """Обробка команди /grant_access @username"""
    # Перевіряємо чи є користувач адміністратором
    if message.from_user.id not in settings.admin_ids_list:
        return # Ігноруємо команду

    # Розбираємо текст команди
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Використання: `/grant_access @username`", parse_mode="Markdown")
        return

    target_username = args[1].strip()
    
    if not target_username.startswith('@'):
        target_username = target_username.lstrip()
    
    try:
        # Шукаємо користувача за username
        target_user = await firestore_client.get_user_by_username(target_username)
        
        if not target_user:
            await message.answer(f"❌ Користувача з username {target_username} не знайдено в базі.")
            return

        target_user_id = target_user.get('user_id')
        
        # Надаємо доступ
        await firestore_client.update_user_access(target_user_id)
        await message.answer(f"✅ Доступ успішно надано для {target_username} (ID: {target_user_id}).")
        
        # Сповіщаємо користувача
        try:
            await bot.send_message(
                target_user_id, 
                f"🎉 {BotReplies.AFTER_PAYMENT_MESSAGE}"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {target_user_id} about access grant: {e}")
            await message.answer(f"⚠️ Доступ надано, але не вдалося надіслати сповіщення користувачу (можливо він заблокував бота).")

    except DatabaseError as e:
        logger.error(f"Database error while granting access: {e}")
        await message.answer("❌ Помилка бази даних при спробі надати доступ.")
    except Exception as e:
        logger.error(f"Unexpected error while granting access: {e}")
        await message.answer("❌ Виникла непередбачувана помилка.")
