from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.main_menu import build_main_menu

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "👋 Welcome to Ever Jobs!\n\n"
        "I can help you find software engineering jobs from "
        "Ukrainian and international job boards.\n\n"
        "🚀 The bot is currently in beta.",
        reply_markup=build_main_menu()
    )