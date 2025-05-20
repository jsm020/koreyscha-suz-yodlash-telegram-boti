import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv
from . import handlers

load_dotenv()
BOT_TOKEN = "7493610692:AAGa6RQnB68XsGVpz-iS85fvKQq6ZKv_he8"
print(BOT_TOKEN)
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set!")

async def main():
    # ✅ 3.7.0+ ga mos Bot
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    handlers.register_handlers(dp)

    print("🤖 Bot ishga tushdi. Kutyapman...")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Xatolik: {e}")
    finally:
        await bot.session.close()
        print("📴 Bot sessiyasi yopildi.")

if __name__ == "__main__":
    asyncio.run(main())
