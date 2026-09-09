from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.database.models import VacancyStatus
from app.keyboards.callbacks import (
    SearchNavigationCallback,
    VacancyActionCallback, SubscriptionCallback,
)


def build_vacancy_actions_keyboard(
    vacancy_id: int,
    status: VacancyStatus,
    *,
    current_index: int | None = None,
    total_jobs: int | None = None,
    subscription_id: int | None = None
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    if status == VacancyStatus.NEW:
        if subscription_id is None:
            rows.append(
                [   InlineKeyboardButton(
                        text="🔔 Subscribe",
                        callback_data=SubscriptionCallback(
                            action="subscribe",
                        ).pack(),
                    ),
                ]
            )
        else:
            rows.append(
                [ InlineKeyboardButton(
                    text="🔕 Unsubscribe",
                    callback_data=SubscriptionCallback(
                        action="unsubscribe",
                        subscription_id=subscription_id,
                    ).pack()
                )]
            )
            rows.append(
                [    InlineKeyboardButton(
                        text="📨 Accept. Send CV",
                        callback_data=VacancyActionCallback(
                            action="applied",
                            vacancy_id=vacancy_id,
                        ).pack(),
                    ),
                    InlineKeyboardButton(
                        text="❌ Reject",
                        callback_data=VacancyActionCallback(
                            action="reject",
                            vacancy_id=vacancy_id,
                        ).pack(),
                    ),
                ]
            )

    elif status == VacancyStatus.APPLIED:
        rows.append(
            [
                InlineKeyboardButton(
                    text="🎤 Job Interview",
                    callback_data=VacancyActionCallback(
                        action="interview",
                        vacancy_id=vacancy_id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=VacancyActionCallback(
                        action="reject",
                        vacancy_id=vacancy_id,
                    ).pack(),
                ),
            ]
        )

    if (
        current_index is not None
        and total_jobs is not None
        and total_jobs > 0
    ):
        navigation_row: list[InlineKeyboardButton] = []

        if current_index > 0:
            navigation_row.append(
                InlineKeyboardButton(
                    text="⬅️ Previous",
                    callback_data=SearchNavigationCallback(
                        action="previous",
                    ).pack(),
                )
            )

        navigation_row.append(
            InlineKeyboardButton(
                text=f"{current_index + 1} / {total_jobs}",
                callback_data=SearchNavigationCallback(
                    action="current",
                ).pack(),
            )
        )

        if current_index < total_jobs - 1:
            navigation_row.append(
                InlineKeyboardButton(
                    text="Next ➡️",
                    callback_data=SearchNavigationCallback(
                        action="next",
                    ).pack(),
                )
            )

        rows.append(navigation_row)

    return InlineKeyboardMarkup(
        inline_keyboard=rows,
    )