from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.bot.templates.responses import send_instagram_invite, send_hypothyroidism_video
import asyncio
import logging
import time # Імпортуємо time для вимірювання часу

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
    logger.info(f"User {callback.from_user.id} started the survey.")
    # Зберігаємо початковий стан
    await state.set_state(SurveyStates.answering)
    await state.update_data(current_question=0, answers=[])
    
    # Відправляємо перше питання
    await send_question(callback.message, 0)
    await callback.answer()

async def send_question(message: Message, question_index: int):
    """Відправляє питання з прогрес-баром"""
    start_time_total = time.time() # Початок вимірювання загального часу
    
    progress_text = f"Прогрес: {question_index + 1}/{len(SURVEY_QUESTIONS)}"
    new_text = f"{progress_text}\n\n{SURVEY_QUESTIONS[question_index]}"

    logger.info(f"Preparing to send question {question_index + 1} (index {question_index}). Text length: {len(new_text)}")

    try:
        api_call_start_time = time.time() # Початок вимірювання часу API-виклику
        await message.edit_text(
            new_text,
            reply_markup=get_survey_keyboard()
        )
        api_call_duration = time.time() - api_call_start_time
        logger.info(f"Successfully edited message for question {question_index + 1}. API call took: {api_call_duration:.4f}s")
    except TelegramBadRequest as e:
        api_call_duration = time.time() - api_call_start_time
        if "message is not modified" in str(e).lower():
            logger.warning(f"Message not modified for question {question_index + 1}. API call took: {api_call_duration:.4f}s. Error: {e}")
        else:
            logger.error(f"TelegramBadRequest error updating question {question_index + 1}. API call took: {api_call_duration:.4f}s. Error: {e}")
            await message.answer(
                new_text,
                reply_markup=get_survey_keyboard()
            )
    except TelegramForbiddenError as e:
        api_call_duration = time.time() - api_call_start_time
        logger.error(f"TelegramForbiddenError: Bot blocked by user or chat not accessible for question {question_index + 1}. API call took: {api_call_duration:.4f}s. Error: {e}")
    except Exception as e:
        api_call_duration = time.time() - api_call_start_time
        logger.error(f"Unexpected error updating question {question_index + 1}. API call took: {api_call_duration:.4f}s. Error: {e}")
        await message.answer(
            new_text,
            reply_markup=get_survey_keyboard()
        )
    
    # Додаємо невелику затримку після будь-якої спроби відправлення/редагування
    await asyncio.sleep(0.1) 
    
    total_duration = time.time() - start_time_total
    logger.info(f"Finished send_question function for question {question_index + 1}. Total duration: {total_duration:.4f}s")


@router.callback_query(SurveyStates.answering, F.data.in_(["answer_yes", "answer_no"]))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    """Обробка відповіді на питання"""
    start_time_process_answer = time.time() # Початок вимірювання часу обробки відповіді
    try:
        # Отримуємо поточний стан
        data = await state.get_data()
        current_question = data["current_question"]
        answers = data["answers"]
        
        logger.info(f"User {callback.from_user.id} answered question {current_question + 1} (index {current_question}). Answer: {callback.data}")

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
            logger.info(f"Moving to next question: {current_question + 2}. Current question index: {current_question + 1}")
            await send_question(callback.message, current_question + 1)
        else:
            logger.info(f"Survey completed by user {callback.from_user.id}. Final answers: {answers}")
            # Завершуємо опитування
            await callback.message.edit_text(
                "Дякую! Ви пройшли опитування 📝💛"
            )

            # Перевіряємо чи є хоча б одна відповідь True
            if any(answers):
                await send_hypothyroidism_video(callback.message)
            else:
                await send_instagram_invite(callback.message)
            
            await state.clear()
        
        await callback.answer() # Важливо викликати callback.answer() для уникнення "годинника" на кнопці
        logger.info(f"Finished process_answer for question {current_question + 1}. Total duration: {time.time() - start_time_process_answer:.4f}s")

    except Exception as e:
        logger.error(f"Error processing answer for user {callback.from_user.id}: {str(e)}")
        await callback.answer("Виникла помилка. Спробуйте ще раз.", show_alert=True)
