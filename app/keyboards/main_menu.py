from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


SEARCH_JOBS_BUTTON = "🔍 Знайти вакансії"
APPLIED_JOBS_BUTTON = "📨 Відправлені резюме"
INTERVIEWS_BUTTON = "🎤 Співбесіди"


def build_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=SEARCH_JOBS_BUTTON),
            ],
            [
                KeyboardButton(text=APPLIED_JOBS_BUTTON),
                KeyboardButton(text=INTERVIEWS_BUTTON),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть дію",
    )