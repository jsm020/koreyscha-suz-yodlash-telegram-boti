
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

# Tooltip va misollar uchun matnlar
HELP_TEXT = (
    "Assalomu alaykum! 👋\n"
    "Koreyscha ↔ o‘zbekcha so‘z juftligini quyidagicha yuboring:\n"
    "\n"
    "🇰🇷 so'z | 🇺🇿 tarjima\n"
    "\n"
    "Misol: 학교 | maktab\n"
    "\n"
    "/takrorlash — kiritilgan so‘zlarni sanasi bo‘yicha ko‘rish va mashq qilish."
)

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(HELP_TEXT)


# So'z juftligini qabul qilish va DBga yozish
import re
from aiogram.types import FSInputFile
from . import db, utils
import aiofiles

WORD_PAIR_REGEX = re.compile(r"^([\uac00-\ud7af\w\s]+)\s*\|\s*([\w\s'’\-]+)$")

@router.message()
async def handle_word_pair(message: Message):
    match = WORD_PAIR_REGEX.match(message.text.strip())
    if not match:
        return  # Faqat so'z juftligi formatiga javob beramiz
    korean, uzbek = match.groups()
    romanized = utils.romanize_korean(korean)
    # Fayl nomini xavfsiz qilish
    safe_korean = ''.join(c for c in korean if c.isalnum())
    audio_filename = f"audio_{message.from_user.id}_{safe_korean}.mp3"
    audio_dir = os.path.join(os.path.dirname(__file__), '..', 'audio')
    audio_path = os.path.abspath(os.path.join(audio_dir, audio_filename))
    utils.generate_korean_audio(korean, audio_path)
    # Audio faylni Telegramga yuklash uchun
    audio_file = FSInputFile(audio_path)
    # DBga yozish
    pool = await db.get_pool()
    word_row = await db.add_word(pool, korean, uzbek, romanized, audio_filename)
    await pool.close()
    await message.answer(f"🇰🇷 {korean}\n🇺🇿 {uzbek}\n✍️ Romanizatsiya: {romanized}")
    await message.answer_audio(audio_file, caption="Koreyscha talaffuz")

# /takrorlash buyrug'i uchun handler (sanalar ro'yxati va so'zlar)
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime

@router.message(Command("takrorlash"))
async def cmd_takrorlash(message: Message):
    pool = await db.get_pool()
    # Unikal sanalar ro'yxatini olish
    async with pool.acquire() as conn:
        dates = await conn.fetch("SELECT created_at, COUNT(*) as cnt FROM words GROUP BY created_at ORDER BY created_at DESC;")
    await pool.close()
    if not dates:
        await message.answer("Hech qanday so'z kiritilmagan.")
        return
    # Tugmalar
    buttons = [[KeyboardButton(text=str(row['created_at'])) for row in dates]]
    markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    text = "Sanani tanlang:\n" + "\n".join([f"{row['created_at']} – {row['cnt']} ta so'z" for row in dates])
    await message.answer(text, reply_markup=markup)


# Mashq (guess-until-mastered) handleri
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class QuizStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_answer = State()

@router.message(F.text.regexp(r"^\d{4}-\d{2}-\d{2}$"))
async def handle_date_select(message: Message, state: FSMContext):
    date = message.text.strip()
    pool = await db.get_pool()
    words = await db.get_words_by_date(pool, date)
    await pool.close()
    if not words:
        await message.answer("Bu kunda so'zlar topilmadi.")
        return
    # So'zlar bo'yicha mashq boshlash
    await state.set_state(QuizStates.waiting_for_answer)
    await state.update_data(words=[dict(w) for w in words], idx=0, correct=[False]*len(words), attempts=[0]*len(words))
    await ask_next_word(message, state)

async def ask_next_word(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data['idx']
    words = data['words']
    correct = data['correct']
    # Keyingi topilmagan so'zni topamiz
    for i in range(len(words)):
        if not correct[i]:
            idx = i
            break
    else:
        # Hamma so'zlar topildi
        await show_quiz_stats(message, state)
        await state.clear()
        return
    await state.update_data(idx=idx)
    await message.answer(f"✍️ Tarjima yozing: {words[idx]['korean']}")

@router.message(QuizStates.waiting_for_answer)
async def handle_quiz_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data['idx']
    words = data['words']
    correct = data['correct']
    attempts = data['attempts']
    pool = await db.get_pool()
    user_id = message.from_user.id
    answer = message.text.strip().lower()
    true_answer = words[idx]['uzbek'].strip().lower()
    attempts[idx] += 1
    is_correct = answer == true_answer
    # Attempts logini DBga yozish
    await db.add_attempt(pool, words[idx]['id'], user_id, attempts[idx], is_correct)
    await pool.close()
    if is_correct:
        correct[idx] = True
        await message.answer("✅ To'g'ri!")
    else:
        await message.answer(f"❌ Noto'g'ri. Yana urinib ko'ring.")
    await state.update_data(correct=correct, attempts=attempts)
    await ask_next_word(message, state)

async def show_quiz_stats(message: Message, state: FSMContext):
    data = await state.get_data()
    words = data['words']
    attempts = data['attempts']
    text = "Mashq tugadi!\n\nNatija:\n"
    for w, a in zip(words, attempts):
        text += f"{w['korean']} – {w['uzbek']} | Urinishlar: {a}\n"
    await message.answer(text)

def register_handlers(dp):
    dp.include_router(router)

