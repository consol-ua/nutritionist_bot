from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.db.firestore import firestore_client
from app.core.exceptions import DatabaseError
from app.bot.keyboards.phone import get_phone_keyboard, remove_keyboard
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
            await message.answer(
                "Вітаю! Ви вже зареєстровані в системі.\n"
                f"Ваш номер телефону: {user_data['phone']}"
            )
            return
            
        await message.answer(
            "Вітаю! Для реєстрації, будь ласка, натисніть кнопку нижче щоб надіслати свій номер телефону.",
            reply_markup=get_phone_keyboard()
        )
        await state.set_state(UserRegistration.waiting_for_phone)
        
    except DatabaseError as e:
        logger.error(f"Помилка при перевірці користувача: {e}")
        await message.answer(
            "❌ Виникла помилка. Спробуйте пізніше."
        )

@router.message(UserRegistration.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    """Обробка отриманого номера телефону"""
    if not message.contact:
        await message.answer(
            "❌ Будь ласка, натисніть кнопку для надсилання номера телефону.",
            reply_markup=get_phone_keyboard()
        )
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
        
        await message.answer(
            "✅ Дякую! Ваш номер телефону успішно збережено.\n"
            "Тепер ви можете користуватися ботом.",
            reply_markup=remove_keyboard()
        )
        await state.clear()
        
    except DatabaseError as e:
        logger.error(f"Помилка при збереженні даних: {e}")
        await message.answer(
            "❌ Виникла помилка при збереженні даних. Спробуйте пізніше.",
            reply_markup=remove_keyboard()
        ) 