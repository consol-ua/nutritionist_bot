from aiogram.types import BotCommand, BotCommandScopeDefault
import logging

logger = logging.getLogger(__name__)

async def set_commands(bot):
    """Встановлює команди бота"""
    try:
        commands = [
            BotCommand(
                command="start",
                description="🏠 На початок"
            ),
            BotCommand(
                command="contact",
                description="📱 Зв'язок зі мною"
            ),
            BotCommand(
                command="about",
                description="ℹ️ Про мене"
            ),
            BotCommand(
                command="menu",
                description="📋 Показати меню"
            )
        ]
        
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("Commands set successfully")
    except Exception as e:
        logger.error(f"Error setting commands: {e}")
        raise 