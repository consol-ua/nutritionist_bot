from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from ...core.exceptions import BotException
import logging

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except BotException as e:
            logger.error(f"Error: {str(e)}")
            if isinstance(event, Message):
                await event.answer("Error. Try again later.")
            elif isinstance(event, CallbackQuery):
                await event.answer("Error. Try again later.", show_alert=True)
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            if isinstance(event, Message):
                await event.answer("Unexpected error. Try again later.")
            elif isinstance(event, CallbackQuery):
                await event.answer("Unexpected error. Try again later.", show_alert=True) 