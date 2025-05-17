from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .. import db

router = Router()

@router.message(F.text == "/takrorlash")
async def cmd_takrorlash(message: types.Message):
    all_words = await db.get_words_by_date(None, None)

    from collections import Counter
    date_counts = Counter(w['created_at'] for w in all_words)

    if not date_counts:
        await message.answer("❌ Hozircha hech qanday so‘z mavjud emas.")
        return

    bot_username = (await message.bot.me()).username
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    for date, count in sorted(date_counts.items()):
        ref_link = f"https://t.me/{bot_username}?start=repeat_{date}_{message.from_user.id}"
        markup.inline_keyboard.append([
            InlineKeyboardButton(text=f"{date} — {count} ta so‘z", callback_data=f"repeat_{date}")
        ])

    await message.answer("📅 Mashq qilmoqchi bo‘lgan sanani tanlang:", reply_markup=markup)

@router.callback_query(F.data.regexp(r"^repeat_\d{4}-\d{2}-\d{2}$"))
async def handle_repeat_callback(callback_query: types.CallbackQuery, state):
    from . import quiz  # Late import — circular importni oldini oladi
    date = callback_query.data.replace("repeat_", "")
    await callback_query.message.answer(f"🧠 {date} sanasidagi mashq boshlandi!")
    await quiz.handle_date_select(callback_query.message, state, override_date=date)
    await callback_query.answer()
