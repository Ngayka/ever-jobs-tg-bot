from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_location_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Без локації",
                callback_data="location:none",
            )
        ],
        [
            InlineKeyboardButton(
                text="Отмена",
                callback_data="location:cancel",
            )
        ],
        ]
    )