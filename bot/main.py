
import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from . import handlers, db

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    # Handlerlarni ro'yxatdan o'tkazish
    handlers.register_handlers(dp)
    print("Bot ishga tushdi!")
    try:
        await dp.start_polling(bot)
    finally:
        await db.close_pool()

if __name__ == "__main__":
    asyncio.run(main())

