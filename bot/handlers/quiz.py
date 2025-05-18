from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import time, os
from .. import db
from aiogram import F

router = Router()

class QuizStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_answer = State()
    waiting_for_known_words_confirm = State()

@router.message(F.text.regexp(r"^\d{4}-\d{2}-\d{2}$"))
async def handle_date_select(message: Message, state: FSMContext, override_date=None):
    date = override_date if override_date else message.text.strip()

    user_id = message.from_user.id
    all_attempts = await db.get_attempts_by_user_and_category(None, user_id, date)
    wrong_word_ids = {row['word_id'] for row in all_attempts if not row['is_correct']}
    attempts_count = {row['word_id']: row['attempt_count'] for row in all_attempts if not row['is_correct']}
    known_word_ids = await db.get_known_word_ids(None, user_id)
    all_words = await db.get_words_by_date(None, date)

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
        await message.answer("Barcha so'zlar yodlangan. Yodlangan so'zlar bilan mashq qilmoqchimisiz? (Ha/Yo'q)", reply_markup=keyboard)
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
    await message.answer(f"Mashq boshlandi! ({len(words)} ta so‘z)", reply_markup=ReplyKeyboardRemove())
    await ask_next_word(message, state)

async def ask_next_word(message: Message, state: FSMContext):
    data = await state.get_data()
    words, correct, attempts = data["words"], data["correct"], data["attempts"]

    for idx, (ok, att) in enumerate(zip(correct, attempts)):
        if not ok and att < 2:
            await state.update_data(idx=idx)
            uzbek = words[idx]["uzbek"]
            progress = [
                "✅" if correct[i] else "❌" if attempts[i] >= 2 else "⬜️"
                for i in range(len(words))
            ]
            progress_lines = [" ".join(progress[i:i+5]) for i in range(0, len(progress), 5)]
            progress_str = "\n".join(progress_lines)

            await message.answer(
                f"✍️ Tarjima yozing: <b>{uzbek}</b> (koreyscha harflarda)\n\n{progress_str}",
                parse_mode="HTML"
            )
            return

    await show_quiz_stats(message, state)

@router.message(QuizStates.waiting_for_answer)
async def handle_quiz_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data["idx"]
    words = data["words"]
    correct = data["correct"]
    attempts = data["attempts"]
    user_id = message.from_user.id

    answer = message.text.strip()
    true_answer = words[idx]["korean"].strip()
    attempts[idx] += 1
    is_correct = (answer == true_answer)

    await db.add_attempt(None, words[idx]["id"], user_id, attempts[idx], is_correct)
    repeat_session_id = data.get("repeat_session_id")
    if repeat_session_id:
        await db.save_repeat_result(None, repeat_session_id, user_id, words[idx]["id"], is_correct, attempts[idx])

    if is_correct:
        correct[idx] = True
        await message.answer("✅ To‘g‘ri!")
        if attempts[idx] == 1:
            await db.add_known_word(None, user_id, words[idx]["id"])
    elif attempts[idx] >= 2:
        await message.answer("❌ Noto‘g‘ri. Keyingi so‘zga o‘tamiz.")
    else:
        await message.answer("❌ Noto‘g‘ri. Yana urinib ko‘ring.")

    await state.update_data(correct=correct, attempts=attempts)
    await ask_next_word(message, state)

@router.message(QuizStates.waiting_for_known_words_confirm)
async def handle_known_words_confirm(message: Message, state: FSMContext):
    javob = message.text.strip().lower()
    if javob not in ["ha", "yo'q", "yo‘q", "yoq"]:
        await message.answer("Iltimos, faqat 'Ha' yoki 'Yo'q' deb javob bering.")
        return

    if javob.startswith("ha"):
        user_id = message.from_user.id
        known_word_ids = await db.get_known_word_ids(None, user_id)
        all_words = await db.get_words_by_date(None, None)
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
        await message.answer(f"Yodlangan so'zlar bilan mashq boshlandi! ({len(words)} ta)", reply_markup=ReplyKeyboardRemove())
        await ask_next_word(message, state)
    else:
        await message.answer("Mashq yakunlandi.", reply_markup=ReplyKeyboardRemove())
        await state.clear()

import os
import time
from aiogram.types import FSInputFile
from ..plot_utils import plot_progress_bar
from .. import db  # db modulni import qilganingizga ishonch hosil qiling

async def show_quiz_stats(message: Message, state: FSMContext):
    data = await state.get_data()
    words = data["words"]
    attempts = data["attempts"]
    correct = data["correct"]
    started_at = data.get("started_at", time.time())
    duration = int(time.time() - started_at)
    user_id = message.from_user.id

    lines = []
    correct_count = 0

    for w, a, ok in zip(words, attempts, correct):
        # ✅ Natijani bazaga saqlash (agar session bor bo‘lsa)

        if ok:
            lines.append(f"✅ {w['korean']} – {w['uzbek']} | {a} urinishda")
            correct_count += 1
        else:
            lines.append(f"❌ {w['korean']} – {w['uzbek']} | Topilmadi (2 urinish)")

    await message.answer(
        f"<b>Mashq tugadi!</b>\n\n" + "\n".join(lines) +
        f"\n\nJami: {len(words)} ta so‘z\n✅ To‘g‘ri: {correct_count}\n⏱ Vaqt: {duration} soniya",
        parse_mode="HTML"
    )

    # 📊 Grafik
    try:
        images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
        os.makedirs(images_dir, exist_ok=True)
        img_path = os.path.join(images_dir, f'progress_{user_id}.png')
        buf = plot_progress_bar(words, correct, attempts)
        with open(img_path, 'wb') as f:
            f.write(buf.read())
        await message.answer_photo(FSInputFile(img_path), caption="📊 Urinishlar grafigi")
        os.remove(img_path)
    except Exception as e:
        await message.answer(f"Grafikda xatolik: {e}")

    await state.clear()
