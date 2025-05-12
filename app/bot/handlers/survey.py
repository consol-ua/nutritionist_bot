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
    
    await message.edit_text(
        f"{progress_text}\n\n"
        f"{SURVEY_QUESTIONS[question_index]}",
        reply_markup=get_survey_keyboard()
    )

@router.callback_query(SurveyStates.answering, F.data.in_(["answer_yes", "answer_no"]))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    """Обробка відповіді на питання"""
    # Отримуємо поточний стан
    data = await state.get_data()
    current_question = data["current_question"]
    answers = data["answers"]
    
    # Зберігаємо відповідь
    answer = callback.data == "answer_yes"
    answers.append(answer)
    
    # Перевіряємо чи це останнє питання
    if current_question + 1 < len(SURVEY_QUESTIONS):
        # Оновлюємо стан
        await state.update_data(
            current_question=current_question + 1,
            answers=answers
        )
        # Відправляємо наступне питання
        await send_question(callback.message, current_question + 1)
    else:
        # Завершуємо опитування
        await callback.message.edit_text(
            "Дякую! Ви пройшли опитування 📝💛"
        )

        # Перевіряємо чи є хоча б одна відповідь True
        if any(answers):
            # Відправляємо відео про гіпотиреоз
            await send_hypothyroidism_video(callback.message)
        else:
            # Відправляємо повідомлення з Instagram
            await send_instagram_invite(callback.message)
        
        # Тут можна додати логіку обробки всіх відповідей
        logger.info(f"User {callback.from_user.id} completed the survey. Answers: {answers}")
        await state.clear()
    
    await callback.answer() 