from aiogram import Router, F
from aiogram.types import Message
import re
from .. import db

router = Router()

@router.message(F.text.regexp(r"^[a-zA-Zа-яА-Яёғқҳўүӣ\s'’\-]+$"))
async def handle_uzbek_query(message: Message):
    query = message.text.lower().strip()
    all_words = await db.get_words_by_date(None, None)
    for w in all_words:
        if w["uzbek"].lower() == query:
            await message.answer(
                f"🇺🇿 {w['uzbek']}\n🇰🇷 {w['korean']}\n✍️ Romanizatsiya: {w['romanized']}"
            )
            return
    await message.answer("❗ Bu so‘z uchun tarjima topilmadi.")