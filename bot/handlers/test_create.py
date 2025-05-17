from aiogram import Router
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from .. import db

router = Router()
ADMIN_USER_IDS = [6848884650]  # Admin ID'ni yangilang

class TestCreateStates(StatesGroup):
    waiting_for_date = State()

@router.message()
async def cmd_create_test(message: Message, state: FSMContext):
    if message.text != "/create_test":
        return

    if message.from_user.id not in ADMIN_USER_IDS:
        await message.answer("Faqat admin test yaratishi mumkin.")
        return

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
    bot_username = (await message.bot.me()).username
    link = f"https://t.me/{bot_username}?start={repeat_key}"
    await message.answer(f"Mana sizning test linkingiz:\n{link}", reply_markup=ReplyKeyboardRemove())
    await state.clear()
