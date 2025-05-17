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
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from . import db, utils
import asyncio
from aiogram.exceptions import TelegramRetryAfter
import time

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
ADMIN_USER_IDS = [6848884650]  # O'zingizning Telegram user_id ni shu yerga yozing

class TestCreateStates(StatesGroup):
    waiting_for_date = State()

@router.message(Command("create_test"))
async def cmd_create_test(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_USER_IDS:
        await message.answer("Faqat admin test yaratishi mumkin.")
        return
    # API orqali sanalar ro'yxatini olamiz
    all_words = await db.get_words_by_date(None, None)
    from collections import Counter
    date_counts = Counter(w['created_at'] for w in all_words)
    if not date_counts:
        await message.answer("Hech qanday sana topilmadi.")
        return
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=date)] for date in date_counts.keys()],
        resize_keyboard=True
    )
    await state.set_state(TestCreateStates.waiting_for_date)
    await message.answer("Qaysi sanadagi so'zlardan test yarataylik?", reply_markup=keyboard)

@router.message(TestCreateStates.waiting_for_date)
async def handle_test_create_date(message: Message, state: FSMContext):
    date = message.text.strip()
    repeat_key = f"repeat_{date}_{message.from_user.id}"
    link = f"https://t.me/{(await message.bot.me()).username}?start={repeat_key}"
    await message.answer(f"Mana sizning test linkingiz:\n{link}", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if message.text and message.text.strip().startswith("/start repeat_"):
        m = re.match(r"/start repeat_(\d{4}-\d{2}-\d{2})_(\d+)", message.text.strip())
        if m:
            date, ref_user_id = m.groups()
            repeat_key = f"repeat_{date}_{ref_user_id}"
            from datetime import datetime
            d = datetime.strptime(date, "%Y-%m-%d").date()
            word_ids = await db.get_or_create_repeat_session(None, repeat_key, d, n=10)
            if not word_ids:
                await message.answer("Bu sana uchun so'zlar topilmadi.")
                return
            all_words = await db.get_words_by_date(None, d)
            id2word = {w['id']: w for w in all_words}
            words = [id2word[i] for i in word_ids if i in id2word]
            await state.set_state(QuizStates.waiting_for_answer)
            await state.update_data(
                words=words,
                idx=0,
                correct=[False] * len(words),
                attempts=[0] * len(words),
                started_at=time.time(),
                date=date,
                repeat_key=repeat_key
            )
            await message.answer("Random mashq boshlandi! (10 ta so'z)", reply_markup=ReplyKeyboardRemove())
            await ask_next_word(message, state)
            return
    await message.answer(HELP_TEXT)
async def safe_answer(message, *args, **kwargs):
    while True:
        try:
            return await message.answer(*args, **kwargs)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)

@router.message(Command("takrorlash"))
async def cmd_takrorlash(message: Message):
    all_words = await db.get_words_by_date(None, None)
    from collections import Counter
    date_counts = Counter(w['created_at'] for w in all_words)
    if not date_counts:
        await safe_answer(message, "Hech qanday so'z kiritilmagan.")
        return
    bot_username = (await message.bot.me()).username
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    lines = []
    for date, cnt in date_counts.items():
        ref_link = f"https://t.me/{bot_username}?start=repeat_{date}_{message.from_user.id}"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"{date} (mashq qilish)", callback_data=f"repeat_{date}")
        ])
        lines.append(f"{date} – {cnt} ta so'z\n<code>{ref_link}</code>")
    await safe_answer(message, "Sanani tanlang:\n" + "\n".join(lines), reply_markup=keyboard, parse_mode="HTML")

class QuizStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_answer = State()
    waiting_for_known_words_confirm = State()

@router.message(F.text.regexp(r"^\\d{4}-\\d{2}-\\d{2}$"))
async def handle_date_select(message: Message, state: FSMContext, override_date=None):
    date = override_date if override_date else message.text.strip()
    user_id = message.from_user.id
    from datetime import datetime
    d = date
    if isinstance(d, str):
        d = datetime.strptime(d, "%Y-%m-%d").date()
    all_attempts = await db.get_attempts_by_user_and_date(None, user_id, d)
    wrong_word_ids = set()
    attempts_count = {}
    for row in all_attempts:
        if not row['is_correct']:
            wrong_word_ids.add(row['word_id'])
            attempts_count[row['word_id']] = row['attempt_count']
    known_word_ids = await db.get_known_word_ids(None, user_id)
    all_words = await db.get_words_by_date(None, date, user_id=None)
    filtered_words = []
    for w in all_words:
        if w['id'] in known_word_ids:
            continue
        if w['id'] in wrong_word_ids:
            w = dict(w)
            w['attempts'] = attempts_count.get(w['id'], 0)
            filtered_words.append(w)
        elif w['id'] not in [row['word_id'] for row in all_attempts]:
            w = dict(w)
            w['attempts'] = 0
            filtered_words.append(w)
    filtered_words.sort(key=lambda w: -w['attempts'])
    words = filtered_words[:10]
    if not words:
        await state.set_state(QuizStates.waiting_for_known_words_confirm)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Ha"), KeyboardButton(text="Yo'q")]],
            resize_keyboard=True
        )
        await message.answer(
            "Barcha so'zlar yodlangan. Yodlangan so'zlar bilan mashq qilishni xohlaysizmi? (Ha/Yo'q)",
            reply_markup=keyboard
        )
        return
    await state.set_state(QuizStates.waiting_for_answer)
    await state.update_data(
        words=[dict(w) for w in words],
        idx=0,
        correct=[False] * len(words),
        attempts=[0] * len(words),
        started_at=time.time(),
        date=date
    )
    await message.answer(f"Mashq boshlandi! (Eng ko'p uringan va oxirgi urinish noto'g'ri bo'lgan {len(words)} ta so'z)", reply_markup=ReplyKeyboardRemove())
    await ask_next_word(message, state)

@router.message(QuizStates.waiting_for_known_words_confirm)
async def handle_known_words_confirm(message: Message, state: FSMContext):
    javob = message.text.strip().lower()
    if javob not in ["ha", "yo'q", "yoq", "yo‘q"]:
        await message.answer("Iltimos, faqat 'Ha' yoki 'Yo'q' deb javob bering.")
        return
    if javob.startswith("ha"):
        user_id = message.from_user.id
        known_word_ids = await db.get_known_word_ids(None, user_id)
        if not known_word_ids:
            await message.answer("Sizda yodlangan so'zlar mavjud emas.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return
        all_words = await db.get_words_by_date(None, None, user_id=None)
        words = [dict(w) for w in all_words if w['id'] in known_word_ids]
        import random
        random.shuffle(words)
        words = words[:10]
        if not words:
            await message.answer("Sizda yodlangan so'zlar mavjud emas.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return
        await state.set_state(QuizStates.waiting_for_answer)
        await state.update_data(
            words=words,
            idx=0,
            correct=[False] * len(words),
            attempts=[0] * len(words),
            started_at=time.time(),
            date=None
        )
        await message.answer(f"Yodlangan so'zlar bilan mashq boshlandi! ({len(words)} ta so'z)", reply_markup=ReplyKeyboardRemove())
        await ask_next_word(message, state)
    else:
        await message.answer("Mashq yakunlandi.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
async def ask_next_word(message: Message, state: FSMContext):
    data = await state.get_data()
    words, correct, attempts = data["words"], data["correct"], data["attempts"]
    for idx, (ok, att) in enumerate(zip(correct, attempts)):
        if not ok and att < 2:
            await state.update_data(idx=idx)
            uzbek = words[idx].get('uzbek')
            progress = []
            for i, w in enumerate(words):
                if correct[i]:
                    progress.append(f"✅ {w['uzbek']}")
                elif attempts[i] >= 2:
                    progress.append(f"❌ {w['uzbek']}")
                else:
                    progress.append(f"⬜️ {w['uzbek']}")
            progress_lines = []
            for i in range(0, len(progress), 5):
                progress_lines.append(' '.join(progress[i:i+5]))
            progress_str = '\n'.join(progress_lines)
            await message.answer(
                f"✍️ Tarjima yozing: {uzbek} (koreyscha harflarda)\n\nProgress:\n{progress_str}"
            )
            return
    await show_quiz_stats(message, state)

@router.message(QuizStates.waiting_for_answer)
async def handle_quiz_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data["idx"]
    words, correct, attempts = data["words"], data["correct"], data["attempts"]
    user_id = message.from_user.id
    repeat_key = data.get("repeat_key")
    answer = message.text.strip()
    true_answer = words[idx]["korean"].strip()
    attempts[idx] += 1
    is_correct = answer == true_answer
    await db.add_attempt(None, words[idx]["id"], user_id, attempts[idx], is_correct)
    if repeat_key:
        await db.save_repeat_result(None, repeat_key, user_id, words[idx]["id"], is_correct, attempts[idx])
    if is_correct:
        correct[idx] = True
        await message.answer("✅ To'g'ri!")
        if attempts[idx] == 1:
            await db.add_known_word(None, user_id, words[idx]["id"])
    elif attempts[idx] >= 2:
        await message.answer(f"❌ Noto'g'ri. Keyingi so'zga o'tamiz.")
    else:
        await message.answer("❌ Noto'g'ri. Yana urinib ko'ring.")
    await state.update_data(correct=correct, attempts=attempts)
    await ask_next_word(message, state)

async def show_quiz_stats(message: Message, state: FSMContext):
    import time
    data = await state.get_data()
    if not all(k in data for k in ("words", "attempts", "correct")):
        await message.answer("Statistika uchun ma'lumot topilmadi.")
        await state.clear()
        return
    words, attempts, correct = data["words"], data["attempts"], data["correct"]
    started_at = data.get("started_at")
    date = data.get("date")
    finished_at = time.time()
    duration = finished_at - started_at if started_at else 0
    repeat_key = data.get("repeat_key")
    user_id = message.from_user.id
    if repeat_key and user_id not in ADMIN_USER_IDS:
        correct_count = sum(1 for ok in correct if ok)
        total = len(words)
        user_mention = message.from_user.mention_html() if hasattr(message.from_user, 'mention_html') else f"<a href='tg://user?id={user_id}'>User</a>"
        admin_text = (
            f"Test natijasi:\n"
            f"Foydalanuvchi: {user_mention} (ID: {user_id})\n"
            f"Test: {repeat_key}\n"
            f"To'g'ri javoblar: {correct_count} / {total}\n"
            f"Urinishlar: {sum(attempts)}\n"
            f"Vaqt: {int(duration)} soniya."
        )
        for admin_id in ADMIN_USER_IDS:
            try:
                await message.bot.send_message(admin_id, admin_text, parse_mode="HTML")
            except Exception:
                pass
    lines = []
    correct_count = 0
    for w, a, ok in zip(words, attempts, correct):
        if ok:
            lines.append(f"✅ {w['korean']} – {w['uzbek']} | Urinishlar: {a}")
            correct_count += 1
        elif a >= 2:
            lines.append(f"❌ {w['korean']} – {w['uzbek']} | Topilmadi (2 urinish)")
    total = len(words)
    await message.answer(
        f"Mashq tugadi!\n\nNatija:\n" + "\n".join(lines) +
        f"\n\nJami: {total} ta so'z. To'g'ri topildi: {correct_count}.\nUrinishlar: {sum(attempts)}.\nVaqt: {int(duration)} soniya."
    )
    try:
        from .plot_utils import plot_progress_bar
        from aiogram.types import FSInputFile
        import os
        user_id = message.from_user.id
        images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
        os.makedirs(images_dir, exist_ok=True)
        img_path = os.path.join(images_dir, f'progress_{user_id}.png')
        buf = plot_progress_bar(words, correct, attempts)
        with open(img_path, 'wb') as f:
            f.write(buf.read())
        await message.answer_photo(photo=FSInputFile(img_path), caption="So'zlar bo'yicha urinishlar grafigi")
        try:
            os.remove(img_path)
        except Exception:
            pass
    except Exception as e:
        await message.answer(f"Grafik chizishda xatolik: {e}")
    user_id = message.from_user.id
    for w, ok, a in zip(words, correct, attempts):
        await db.add_attempt(None, w['id'], user_id, a, ok)
    from datetime import datetime
    d = date
    if isinstance(d, str):
        d = datetime.strptime(d, "%Y-%m-%d").date()
    prev_stats = await db.get_attempts_by_user_and_date(None, user_id, d)
    prev_correct = sum(1 for row in prev_stats if row['is_correct'])
    await message.answer(f"Oldingi mashqda to'g'ri topilgan so'zlar: {prev_correct} ta.")

# So‘z juftligini qabul qilish va o‘zbekcha so‘rov
@router.message()
async def handle_word_pair_or_uzbek_query(message: Message):
    text = message.text.strip()
    match = WORD_PAIR_REGEX.match(text)
    if match:
        korean, uzbek = match.groups()
        romanized = utils.romanize_korean(korean)
        safe_korean = "".join(c for c in korean if c.isalnum())
        audio_filename = f"audio_{message.from_user.id}_{safe_korean}.mp3"
        audio_path = AUDIO_DIR / audio_filename
        utils.generate_korean_audio(korean, str(audio_path))
        audio_file = FSInputFile(str(audio_path))
        await db.add_word(None, korean, uzbek, romanized, audio_filename)
        await safe_answer(
            message,
            f"🇰🇷 {korean}\n🇺🇿 {uzbek}\n✍️ Romanizatsiya: {romanized}"
        )
        await message.answer_audio(audio_file, caption="Koreyscha talaffuz")
        return

    # O'zbekcha so'rov: faqat harf va bo'shliqdan iborat bo'lsa, so'rov deb hisoblaymiz
    uzbek_query = text.lower()
    if re.match(r"^[a-zA-Zа-яА-Яёғқўҳүўӣӣўқҳ\s'’\-]+$", uzbek_query):
        all_words = await db.get_words_by_date(None, None)
        found = None
        for w in all_words:
            if w['uzbek'].lower() == uzbek_query:
                found = w
                break
        if found:
            await safe_answer(
                message,
                f"🇺🇿 {uzbek_query}\n🇰🇷 {found['korean']}\n✍️ Romanizatsiya: {found['romanized']}"
            )
        else:
            await safe_answer(message, "Bu so'z uchun koreyscha tarjima topilmadi.")

# Router ro‘yxatdan o‘tishi
def register_handlers(dp):
    dp.include_router(router)

# Inline tugma uchun callback handler (mashqni ochish)
from aiogram import types
@router.callback_query(F.data.regexp(r"^repeat_\\d{4}-\\d{2}-\\d{2}$"))
async def handle_repeat_callback(callback_query: types.CallbackQuery, state: FSMContext):
    date = callback_query.data.replace("repeat_", "")
    await callback_query.message.answer(f"{date} sanasidagi mashq boshlandi!")
    await handle_date_select(callback_query.message, state, override_date=date)
    await callback_query.answer()