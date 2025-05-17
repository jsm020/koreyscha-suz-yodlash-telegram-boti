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

    # Agar start link orqali kelingan bo‘lsa
    m = re.match(r"/start repeat_(\d{4}-\d{2}-\d{2})_(\d+)", text)
    if m:
        date_str, ref_user_id = m.groups()
        repeat_key = f"repeat_{date_str}_{ref_user_id}"
        try:
            session_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            await message.answer("❌ Sana noto‘g‘ri formatda.")
            return

        session = await db.get_or_create_repeat_session(None, repeat_key, session_date)
        word_ids = session.get("words", [])
        if not word_ids:
            await message.answer("❌ Bu sana uchun so‘zlar topilmadi.")
            return

        all_words = await db.get_words_by_date(None, session_date)
        id2word = {w["id"]: w for w in all_words}
        words = [id2word[i] for i in word_ids if i in id2word]
        if not words:
            await message.answer("❌ So‘zlar topilmadi.")
            return

        await state.set_state(QuizStates.waiting_for_answer)
        await state.update_data(
            words=words,
            idx=0,
            correct=[False] * len(words),
            attempts=[0] * len(words),
            started_at=time.time(),
            date=date_str,
            repeat_key=repeat_key,
            repeat_session_id=session["id"]
        )
        await message.answer(f"✅ Random mashq boshlandi! ({len(words)} ta)")
        await ask_next_word(message, state)
        return

    # Fallback — oddiy /start uchun
    await message.answer(
        "👋 Assalomu alaykum!\n"
        "Mashqlarni boshlash uchun /takrorlash buyrug‘ini bosing yoki sizga yuborilgan test havolasini tanlang."
    )
