from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.db.firestore import firestore_client
from app.core.exceptions import DatabaseError
from app.bot.templates.responses import (
    send_welcome_video,
    send_welcome_message,
    send_registration_request,
    send_error_message,
    send_database_error
)
from google.cloud import firestore
import logging

logger = logging.getLogger(__name__)
router = Router()

class UserRegistration(StatesGroup):
    waiting_for_phone = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обробка команди /start"""
    try:
        # Перевіряємо чи користувач вже зареєстрований
        user_data = await firestore_client.get_user(message.from_user.id)
        
        if user_data and user_data.get('phone'):
            await send_welcome_video(message)
            await send_welcome_message(message)
            return
            
        await send_registration_request(message)
        await state.set_state(UserRegistration.waiting_for_phone)
        
    except DatabaseError as e:
        logger.error(f"Помилка при перевірці користувача: {e}")
        await send_error_message(message)

@router.message(UserRegistration.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    """Обробка отриманого номера телефону"""
    if not message.contact:
        await send_registration_request(message)
        return
    
    phone = message.contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone
    
    try:
        # Зберігаємо дані користувача
        user_data = {
            'user_id': message.from_user.id,
            'phone': phone,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'registered_at': firestore.SERVER_TIMESTAMP
        }
        
        await firestore_client.save_user(message.from_user.id, user_data)
        await send_welcome_video(message)
        await send_welcome_message(message)
        await state.clear()
        
    except DatabaseError as e:
        logger.error(f"Помилка при збереженні даних: {e}")
        await send_database_error(message) 