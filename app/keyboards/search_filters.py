from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.docs.job_sources import SourceGroup
from app.keyboards.callbacks import (
    SourceTypeCallback, SourceGroupCallback,
)
from app.search_filters import (SourceSelection)


def build_source_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇺🇦 Ukraine",
                    callback_data=SourceGroupCallback(
                        source_group=SourceGroup.UKRAINE,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇦 Odoo Vacations Ukraine",
                    callback_data=SourceGroupCallback(
                        source_group=SourceGroup.ODOO_UKRAINE,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌏 Odoo World",
                    callback_data=SourceGroupCallback(
                        source_group=SourceGroup.ODOO_WORLD,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="🌍 Worldwide (Job Boards)",
                    callback_data=SourceGroupCallback(
                        source_group=SourceGroup.JOB_BOARDS_WW,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="💼 LinkedIn (Job Boards)",
                    callback_data=SourceGroupCallback(
                        source_group=SourceGroup.LINKEDIN,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="💼 Remote First Jobs (Job Boards)",
                    callback_data=SourceGroupCallback(
                        source_group=SourceGroup.REMOTEFIRSTJOBS,
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
                    text="🏢 Odoo Companies",
                    callback_data=SourceTypeCallback(
                        source_type=SourceSelection.COMPANIES,
                    ).pack(),
                ),
            ],
        ],
    )