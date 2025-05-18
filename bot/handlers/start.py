from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from .quiz import ask_next_word, QuizStates
from .. import db
import re, time

router = Router()

@router.message(Command("start"))
async def handle_start_command(message: Message, state: FSMContext):
    text = message.text.strip()

    # Agar start link orqali: kategoriya asosida
    m_cat = re.match(r"/start repeatcat_(.+)", text)
    if m_cat:

        category_name = m_cat.group(1)
        repeat_key = f"repeatcat_{category_name}"
        session = await db.get_or_create_repeat_session_by_category(None, repeat_key, category_name)
        repeat_session_id = session['id']
        words = await db.get_words_by_category(None, category_name)

        if not words:
            await message.answer("❌ Ushbu kategoriya uchun so‘zlar topilmadi.")
            return

        await state.set_state(QuizStates.waiting_for_answer)
        await state.update_data(
            words=words,
            idx=0,
            correct=[False] * len(words),
            attempts=[0] * len(words),
            started_at=time.time(),
            category=category_name,
            repeat_session_id = repeat_session_id
        )
        await message.answer(f"✅ '{category_name}' kategoriyasi uchun mashq boshlandi! ({len(words)} ta)")
        await ask_next_word(message, state)
        return

    # Oddiy /start
    await message.answer(
        "👋 Assalomu alaykum!\n"
        "Mashqlarni boshlash uchun /takrorlash buyrug‘ini bosing yoki sizga yuborilgan test havolasini tanlang."
    )
