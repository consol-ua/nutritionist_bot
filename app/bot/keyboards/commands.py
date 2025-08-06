from aiogram.types import BotCommand, BotCommandScopeDefault
import logging
from app.bot.texts.replies import BotReplies

logger = logging.getLogger(__name__)

async def set_commands(bot):
    """Встановлює команди бота"""
    try:
        commands = [
            BotCommand(
                command="start",
                description=BotReplies.START_DESCRIPTION
            ),
            BotCommand(
                command="content",
                description=BotReplies.CONTENT_DESCRIPTION
            ),
            BotCommand(
                command="about",
                description=BotReplies.ABOUT_DESCRIPTION
            ),
            BotCommand(
                command="contact",
                description=BotReplies.CONTACT_DESCRIPTION
            ),
            BotCommand(
                command="getfileid",
                description="Отримати file_id файлу (тимчасова команда)"
            )

        ]
        
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    except Exception as e:
        logger.error(f"Error setting commands: {e}")
        raise 