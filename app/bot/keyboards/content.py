from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_content_keyboard() -> ReplyKeyboardMarkup:
    """Створює клавіатуру з кнопками контенту"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Контент 1")],
            [KeyboardButton(text="Контент 2")],
            [KeyboardButton(text="Контент 3")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard 