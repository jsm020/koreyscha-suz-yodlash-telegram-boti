import os
import re
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from . import db, utils

# ──────────────────────────── Konstantalar ────────────────────────────
HELP_TEXT = (
    "Assalomu alaykum! 👋\n"
    "Koreyscha ↔ o‘zbekcha so‘z juftligini quyidagicha yuboring:\n\n"
    "🇰🇷 so'z | 🇺🇿 tarjima\n"
    "Misol: 학교 | maktab\n\n"
    "/takrorlash — kiritilgan so‘zlarni sanasi bo‘yicha ko‘rish va mashq qilish."
)

WORD_PAIR_REGEX = re.compile(
    r"^([\uac00-\ud7af\w\s]+)\s*\|\s*([\w\s'’\-]+)$", re.UNICODE
)

AUDIO_DIR = Path(__file__).resolve().parent.parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

router = Router()

# ──────────────────────────── /start ────────────────────────────
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(HELP_TEXT)

# ──────────────────────────── /takrorlash ───────────────────────
@router.message(Command("takrorlash"))
async def cmd_takrorlash(message: Message):
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        dates = await conn.fetch(
            """
            SELECT to_char(created_at, 'YYYY-MM-DD') AS created_at,
                   COUNT(*)                       AS cnt
            FROM   words
            GROUP  BY created_at
            ORDER  BY created_at DESC;
            """
        )

    if not dates:
        await message.answer("Hech qanday so'z kiritilmagan.")
        return

    buttons = [[KeyboardButton(text=row["created_at"])] for row in dates]
    markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    lines = [f"{row['created_at']} – {row['cnt']} ta so'z" for row in dates]
    await message.answer("Sanani tanlang:\n" + "\n".join(lines), reply_markup=markup)

# ──────────────────────────── FSM holatlari ─────────────────────
class QuizStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_answer = State()

# ──────────────────────────── Sana tanlash ──────────────────────
@router.message(F.text.regexp(r"^\d{4}-\d{2}-\d{2}$"))
async def handle_date_select(message: Message, state: FSMContext):
    date = message.text.strip()
    pool = await db.get_pool()
    words = await db.get_words_by_date(pool, date)

    if not words:
        await message.answer("Bu kunda so'zlar topilmadi.")
        return

    await state.set_state(QuizStates.waiting_for_answer)
    await state.update_data(
        words=[dict(w) for w in words],
        idx=0,
        correct=[False] * len(words),
        attempts=[0] * len(words),
    )
    await ask_next_word(message, state)

# ──────────────────────────── Keyingi savol ─────────────────────
async def ask_next_word(message: Message, state: FSMContext):
    data = await state.get_data()
    words, correct, attempts = data["words"], data["correct"], data["attempts"]
    # Avval 2 martadan ko'p noto'g'ri topilganlarni o'tkazib yuborish uchun flag
    for idx, (ok, att) in enumerate(zip(correct, attempts)):
        if not ok and att < 2:
            await state.update_data(idx=idx)
            await message.answer(f"✍️ Tarjima yozing: {words[idx]['korean']}")
            return

    # Hamma so'zlar to'g'ri topildimi yoki 2 martadan ko'p noto'g'ri topilganlar bormi?
    # Endi 2 martadan ko'p noto'g'ri topilganlarni yakuniy statistikaga qo'shish
    await show_quiz_stats(message, state)
    await state.clear()

# ──────────────────────────── Javob tekshirish ──────────────────
@router.message(QuizStates.waiting_for_answer)
async def handle_quiz_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data["idx"]
    words, correct, attempts = data["words"], data["correct"], data["attempts"]

    user_id = message.from_user.id
    answer = message.text.strip().lower()
    true_answer = words[idx]["uzbek"].strip().lower()

    attempts[idx] += 1
    is_correct = answer == true_answer

    pool = await db.get_pool()
    await db.add_attempt(pool, words[idx]["id"], user_id, attempts[idx], is_correct)

    if is_correct:
        correct[idx] = True
        await message.answer("✅ To'g'ri!")
    elif attempts[idx] >= 2:
        await message.answer(f"❌ Noto'g'ri. Keyingi so'zga o'tamiz.")
    else:
        await message.answer("❌ Noto'g'ri. Yana urinib ko'ring.")

    await state.update_data(correct=correct, attempts=attempts)
    await ask_next_word(message, state)

# ──────────────────────────── Statistikani ko‘rsatish ───────────
async def show_quiz_stats(message: Message, state: FSMContext):
    data = await state.get_data()
    words, attempts, correct = data["words"], data["attempts"], data["correct"]

    lines = []
    for w, a, ok in zip(words, attempts, correct):
        if ok:
            lines.append(f"{w['korean']} – {w['uzbek']} | Urinishlar: {a}")
        elif a >= 2:
            lines.append(f"{w['korean']} – {w['uzbek']} | Topilmadi (2 urinish)")
    await message.answer("Mashq tugadi!\n\nNatija:\n" + "\n".join(lines))

# ──────────────────────────── So‘z juftligini qabul qilish ─────
@router.message()
async def handle_word_pair(message: Message):
    match = WORD_PAIR_REGEX.match(message.text.strip())
    if not match:
        return

    korean, uzbek = match.groups()
    romanized = utils.romanize_korean(korean)

    safe_korean = "".join(c for c in korean if c.isalnum())
    audio_filename = f"audio_{message.from_user.id}_{safe_korean}.mp3"
    audio_path = AUDIO_DIR / audio_filename

    utils.generate_korean_audio(korean, str(audio_path))

    audio_file = FSInputFile(str(audio_path))

    pool = await db.get_pool()
    await db.add_word(pool, korean, uzbek, romanized, audio_filename)

    await message.answer(
        f"🇰🇷 {korean}\n🇺🇿 {uzbek}\n✍️ Romanizatsiya: {romanized}"
    )
    await message.answer_audio(audio_file, caption="Koreyscha talaffuz")

# ──────────────────────────── Router ro‘yxatdan o‘tishi ─────────
def register_handlers(dp):
    dp.include_router(router)
