from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


SEARCH_JOBS_BUTTON = "🔍 Let's find your next job"
APPLIED_JOBS_BUTTON = "📨 Sent CV's"
INTERVIEWS_BUTTON = "🎤 Job's interviews"


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
        input_field_placeholder="Choose an action",
    )