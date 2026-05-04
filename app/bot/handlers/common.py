from aiogram import Router, types, F
from aiogram.filters import Command
import logging
from app.services.scheduler import scheduler


logger = logging.getLogger(__name__)
router = Router()

@router.message(F.document | F.photo | F.video | F.audio | F.voice | F.video_note)
async def handle_file(message: types.Message):
    """Обробник для файлів різних типів"""
    file_id = None
    file_type = None
    
    if message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.photo:
        file_id = message.photo[-1].file_id  # Беремо найбільше фото
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    elif message.voice:
        file_id = message.voice.file_id
        file_type = "voice"
    elif message.video_note:
        file_id = message.video_note.file_id
        file_type = "video_note"
    
    if file_id:
        await message.answer(
            f"✅ File received!\n"
            f"Type: {file_type}\n"
            f"File ID: {file_id}"
        )

@router.message(Command("getfileid"))
async def get_file_id(message: types.Message):
    """Тимчасовий хендлер для отримання file_id"""
    await message.answer(
        "📤 Відправте файл (відео, фото, документ), щоб отримати його file_id.\n"
        "Цей file_id можна використовувати в налаштуваннях бота."
    )

@router.message(F.text == "scheduler")
async def handle_content_selection(message: types.Message):
    jobs = scheduler.get_all_jobs()
    
    await message.answer(f'{jobs}') 