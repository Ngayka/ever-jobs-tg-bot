import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import settings
from app.handlers.start import router as start_router
from app.handlers.search import router as search_router


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()

    dispatcher.include_router(start_router)
    dispatcher.include_router(search_router)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())