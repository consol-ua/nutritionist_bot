from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.config import get_settings
from app.bot.texts.replies import BotReplies
from app.bot.texts.buttons import BotButtons
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

CONTENT_DATA = [
    # content_1
    {
        "video": settings.VIDEO_1_ID,
        "doc": settings.DOC_1_ID,
        "prev": None,
        "next": "conten_2"
    },
    # content_2
    {
        "video": settings.VIDEO_2_ID,
        "doc": None,
        "prev": "conten_1",
        "next": "conten_3"
    },
    # content_3
    {
        "video": settings.VIDEO_3_ID,
        "doc": settings.DOC_3_ID,
        "prev": "conten_2",
        "next": "conten_4"
    },
    # content_4
    {
        "video": settings.VIDEO_4_ID,
        "doc": settings.DOC_4_ID,
        "prev": "conten_3",
        "next": "conten_5"
    },
    # content_5
    {
        "video": settings.VIDEO_5_ID,
        "doc": settings.DOC_5_ID,
        "prev": "conten_4",
        "next": "conten_6"
    },
    # content_6
    {
        "video": settings.VIDEO_6_ID,
        "doc": settings.DOC_6_ID,
        "prev": "conten_5",
        "next": "conten_7"
    },
    # content_7
    {
        "video": settings.VIDEO_7_ID,
        "doc": None,
        "prev": "conten_6",
        "next": None
    }
]

async def send_content(message: Message, idx: int):
    data = CONTENT_DATA[idx]
    await message.answer_video(video=data["video"], protect_content=True)
    if data["doc"]:
        await message.answer_document(document=data["doc"], protect_content=True)

    buttons = []
    if data["prev"]:
        buttons.append(InlineKeyboardButton(
            text=BotButtons.PREVIOUS_VIDEO,
            callback_data=data["prev"]
        ))
    if data["next"]:
        buttons.append(InlineKeyboardButton(
            text=BotButtons.NEXT_VIDEO,
            callback_data=data["next"]
        ))

    if buttons:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
        await message.answer(BotReplies.CONTENT_NAVIGATION, reply_markup=keyboard)

async def send_content_bonus_1(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=BotButtons.GO_TO_GROUP,
                url=settings.CLOSED_TELEGRAM_GROUP
            )]
        ]
    )
    await message.answer(BotReplies.CLOSED_TELEGRAM_GROUP, reply_markup=keyboard)

async def send_content_bonus_2(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=BotButtons.INSTAGRAM_BUTTON_TEXT,
                url=BotButtons.INSTAGRAM_URL
            )]
        ]
    )
    await message.answer(BotReplies.DISCONT_DESCRIPTION, parse_mode="Markdown", reply_markup=keyboard)