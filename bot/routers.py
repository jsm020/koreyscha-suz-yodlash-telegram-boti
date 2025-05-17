from aiogram import Router
from .handlers import start, query, quiz, repeat_menu, test_create

router = Router()
router.include_routers(
    start.router,
    query.router,
    quiz.router,
    repeat_menu.router,
    test_create.router,
)
