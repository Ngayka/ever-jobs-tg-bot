import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import settings
from app.database.session import create_tables
from app.handlers.start import router as start_router
from app.handlers.search import router as search_router
from app.handlers.vacancy_actions import (
    router as vacancy_actions_router,
)
from app.handlers.tracked_vacancies import (
    router as tracked_vacancies_router,
)
from app.handlers.search_navigation import (router as search_navigation_router,
)
from app.handlers.subscriptions import (
    router as subscriptions_router,
)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    await create_tables()
    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()

    dispatcher.include_router(start_router)
    dispatcher.include_router(search_router)
    dispatcher.include_router(vacancy_actions_router)
    dispatcher.include_router(tracked_vacancies_router)
    dispatcher.include_router(search_navigation_router)
    dispatcher.include_router(subscriptions_router)


    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())