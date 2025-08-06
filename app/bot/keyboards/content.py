from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.texts.buttons import BotButtons
from typing import Optional

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

# def get_welcome_keyboard() -> InlineKeyboardMarkup:
#     """Створює inline клавіатуру з кнопками контенту"""
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text=BotButtons.WELCOM_BTN_1, callback_data="welcome_btn_1")],
#             [InlineKeyboardButton(text=BotButtons.WELCOM_BTN_2, callback_data="welcome_btn_2")],
#             [InlineKeyboardButton(text=BotButtons.WELCOM_BTN_3, callback_data="welcome_btn_3")]
#         ]
#     )
#     return keyboard

def get_welcome_keyboard(exclude_button: Optional[str] = "welcome_btn_1") -> InlineKeyboardMarkup:
    buttons_data = [
        {"text": BotButtons.WELCOM_BTN_1, "callback_data": "welcome_btn_1"},
        {"text": BotButtons.WELCOM_BTN_2, "callback_data": "welcome_btn_2"},
        {"text": BotButtons.WELCOM_BTN_3, "callback_data": "welcome_btn_3"}
    ]

    filtered_buttons = [
        InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"])
        for btn in buttons_data
        if btn["callback_data"] != exclude_button
    ]

    inline_keyboard = [filtered_buttons]

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard
