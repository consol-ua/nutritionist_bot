from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Створює клавіатуру з кнопкою для запросу номера телефону"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Надіслати номер телефону", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def remove_keyboard() -> ReplyKeyboardRemove:
    """Прибирає клавіатуру"""
    return ReplyKeyboardRemove() 