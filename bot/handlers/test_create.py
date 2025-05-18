from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from .. import db

router = Router()
ADMIN_USER_IDS = [6848884650]  # Admin ID'ni yangilang

class TestCreateStates(StatesGroup):
    waiting_for_category = State()

@router.message(Command("create_test"))
async def cmd_create_test(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_USER_IDS:
        await message.answer("❌ Faqat admin test yaratishi mumkin.")
        return

    all_categories = await db.get_all_categories()  # yangi funksiya kerak

    if not all_categories:
        await message.answer("❗ Hech qanday kategoriya topilmadi.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat['name'])] for cat in all_categories],
        resize_keyboard=True
    )

    await state.set_state(TestCreateStates.waiting_for_category)
    await message.answer("📂 Quyidagi kategoriyalardan birini tanlang:", reply_markup=keyboard)

@router.message(TestCreateStates.waiting_for_category)
async def handle_test_create_category(message: Message, state: FSMContext):
    category_name = message.text.strip()
    bot_username = (await message.bot.me()).username
    link = f"https://t.me/{bot_username}?start=repeatcat_{category_name}"
    await message.answer(f"✅ Mana sizning test linkingiz:\n<code>{link}</code>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    await state.clear()