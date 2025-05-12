from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Створює клавіатуру головного меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Зв'язок зі мною")],
            [KeyboardButton(text="Про мене")],
            [KeyboardButton(text="На головну")]
        ],
        resize_keyboard=True
    )
    return keyboard 