from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.job_sources import Region, SourceType
from app.keyboards.callbacks import (
    RegionCallback,
    SourceTypeCallback,
)
from app.search_filters import (SourceSelection)


def build_region_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇺🇦 Ukraine",
                    callback_data=RegionCallback(
                        region=Region.UKRAINE,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="🇪🇺 Europe",
                    callback_data=RegionCallback(
                        region=Region.EUROPE,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇸 USA & Canada",
                    callback_data=RegionCallback(
                        region=Region.NORTH_AMERICA,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌏 Asia",
                    callback_data=RegionCallback(
                        region=Region.ASIA,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="🌍 Worldwide",
                    callback_data=RegionCallback(
                        region=Region.WORLDWIDE,
                    ).pack(),
                ),
            ],
        ],
    )


def build_source_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔎 Job boards",
                    callback_data=SourceTypeCallback(
                        source_type=SourceSelection.JOB_BOARDS,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏢 Companies",
                    callback_data=SourceTypeCallback(
                        source_type=SourceSelection.COMPANIES,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⭐ All recommended",
                    callback_data=SourceTypeCallback(
                        source_type=SourceSelection.ALL,
                    ).pack(),
                ),
            ],
        ],
    )