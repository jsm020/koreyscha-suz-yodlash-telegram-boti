from aiogram import Dispatcher

# Barcha modul routerlarini import qilamiz
from . import (
    start,
    # query,
    quiz,
    repeat_menu,
    test_create
)

def register_handlers(dp: Dispatcher):
    # dp.include_router(query.router)
    dp.include_router(quiz.router)
    dp.include_router(repeat_menu.router)
    dp.include_router(test_create.router)
    dp.include_router(start.router)
