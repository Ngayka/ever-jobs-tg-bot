from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.database.models import VacancyStatus
from app.keyboards.callbacks import VacancyActionCallback


def build_vacancy_actions_keyboard(
    vacancy_id: int,
    status: VacancyStatus,
) -> InlineKeyboardMarkup | None:
    if status == VacancyStatus.NEW:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📨 Відправила резюме",
                        callback_data=VacancyActionCallback(
                            action="applied",
                            vacancy_id=vacancy_id,
                        ).pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Відхилити",
                        callback_data=VacancyActionCallback(
                            action="reject",
                            vacancy_id=vacancy_id,
                        ).pack(),
                    ),
                ],
            ],
        )

    if status == VacancyStatus.APPLIED:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🎤 Співбесіда",
                        callback_data=VacancyActionCallback(
                            action="interview",
                            vacancy_id=vacancy_id,
                        ).pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Відхилити",
                        callback_data=VacancyActionCallback(
                            action="reject",
                            vacancy_id=vacancy_id,
                        ).pack(),
                    ),
                ],
            ],
        )

    return None
