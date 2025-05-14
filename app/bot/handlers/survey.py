from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.bot.templates.responses import send_instagram_invite, send_hypothyroidism_video
import logging

logger = logging.getLogger(__name__)
router = Router()

class SurveyStates(StatesGroup):
    """Стани для опитування"""
    answering = State()

# Питання опитування
SURVEY_QUESTIONS = [
    "Ви набираєте вагу без будь-яких на те причин (складно схуднути)",
    "Руки, ноги і тіло мерзнуть без жодних причин",
    "Відчуваєте постійну втому, після їжі хочеться спати",
    "Проблеми з концентрацією, \"туман в голові\" / зниження пам'яті, складно зосередитись",
    "Турбують набряки та закреп",
    "Сухість шкіри, ламкість та випадіння волосся",
    "Рідшають брови"
]

def get_survey_keyboard() -> InlineKeyboardMarkup:
    """Створює клавіатуру з кнопками Так/Ні"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Так", callback_data="answer_yes"),
                InlineKeyboardButton(text="❌ Ні", callback_data="answer_no")
            ]
        ]
    )

@router.callback_query(F.data == "start_survey")
async def start_survey(callback: CallbackQuery, state: FSMContext):
    """Початок опитування"""
    # Зберігаємо початковий стан
    await state.set_state(SurveyStates.answering)
    await state.update_data(current_question=0, answers=[])
    
    # Відправляємо перше питання
    await send_question(callback.message, 0)
    await callback.answer()

async def send_question(message: Message, question_index: int):
    """Відправляє питання з прогрес-баром"""
    progress_text = f"Прогрес: {question_index + 1}/{len(SURVEY_QUESTIONS)}"
    new_text = f"{progress_text}\n\n{SURVEY_QUESTIONS[question_index]}"
    
    try:
        await message.edit_text(
            new_text,
            reply_markup=get_survey_keyboard()
        )
    except Exception as e:
        logger.error(f"Error updating question: {str(e)}")
        # Спробуємо відправити нове повідомлення якщо редагування не вдалося
        await message.answer(
            new_text,
            reply_markup=get_survey_keyboard()
        )

@router.callback_query(SurveyStates.answering, F.data.in_(["answer_yes", "answer_no"]))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    """Обробка відповіді на питання"""
    try:
        # Отримуємо поточний стан
        data = await state.get_data()
        current_question = data["current_question"]
        answers = data["answers"]
        
        # Зберігаємо відповідь
        answer = callback.data == "answer_yes"
        answers.append(answer)
        
        # Оновлюємо стан асинхронно
        await state.update_data(
            current_question=current_question + 1,
            answers=answers
        )
        
        # Перевіряємо чи це останнє питання
        if current_question + 1 < len(SURVEY_QUESTIONS):
            # Відправляємо наступне питання
            await send_question(callback.message, current_question + 1)
        else:
            # Завершуємо опитування
            await callback.message.edit_text(
                "Дякую! Ви пройшли опитування 📝💛"
            )

            # Перевіряємо чи є хоча б одна відповідь True
            if any(answers):
                await send_hypothyroidism_video(callback.message)
            else:
                await send_instagram_invite(callback.message)
            
            logger.info(f"User {callback.from_user.id} completed the survey. Answers: {answers}")
            await state.clear()
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error processing answer: {str(e)}")
        await callback.answer("Виникла помилка. Спробуйте ще раз.", show_alert=True) 