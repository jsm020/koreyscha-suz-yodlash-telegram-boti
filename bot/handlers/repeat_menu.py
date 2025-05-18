from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .. import db

router = Router()

@router.message(F.text == "/takrorlash")
async def cmd_takrorlash(message: types.Message):
    all_categories = await db.get_all_categories()
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    for cat in all_categories:
        category_id = cat['id']
        category_name = cat['name']
        markup.inline_keyboard.append([
            InlineKeyboardButton(text=f"🏷 {category_name}", callback_data=f"{category_name}")
        ])

    await message.answer("📂 Kategoriyalardan birini tanlang:", reply_markup=markup)

@router.callback_query()
async def handle_repeat_callback(callback_query: types.CallbackQuery, state):
    text = callback_query.data    
    from . import quiz  # Late import — circular importni oldini oladi
    await callback_query.message.answer(f"🧠 {text} categoriyasi bo'icha mashq boshlandi!")
    await quiz.handle_date_select(callback_query.message, state, override_date=text)
    await callback_query.answer()
