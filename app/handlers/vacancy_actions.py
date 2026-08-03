from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.database.models import VacancyStatus
from app.database.repository import vacancy_repository
from app.keyboards.callbacks import VacancyActionCallback
from app.keyboards.vacancy_actions import (
    build_vacancy_actions_keyboard,
)


router = Router()


@router.callback_query(
    VacancyActionCallback.filter(
        F.action == "reject",
    )
)
async def handle_reject_vacancy(
    callback: CallbackQuery,
    callback_data: VacancyActionCallback,
) -> None:
    vacancy = await vacancy_repository.set_status(
        vacancy_id=callback_data.vacancy_id,
        telegram_user_id=callback.from_user.id,
        status=VacancyStatus.REJECTED,
    )

    if vacancy is None:
        await callback.answer(
            "Вакансію не знайдено.",
            show_alert=True,
        )
        return

    await callback.answer("Вакансію відхилено")

    if callback.message:
        await callback.message.edit_reply_markup(
            reply_markup=None,
        )

        await callback.message.answer(
            f"❌ Відхилено: {vacancy.title}"
        )


@router.callback_query(
    VacancyActionCallback.filter(
        F.action == "applied",
    )
)
async def handle_applied_vacancy(
    callback: CallbackQuery,
    callback_data: VacancyActionCallback,
) -> None:
    vacancy = await vacancy_repository.set_status(
        vacancy_id=callback_data.vacancy_id,
        telegram_user_id=callback.from_user.id,
        status=VacancyStatus.APPLIED,
    )

    if vacancy is None:
        await callback.answer(
            "Вакансію не знайдено.",
            show_alert=True,
        )
        return

    await callback.answer("Збережено як «Відправила резюме»")

    if callback.message:
        await callback.message.edit_reply_markup(
            reply_markup=build_vacancy_actions_keyboard(
                vacancy_id=vacancy.id,
                status=vacancy.status,
            ),
        )

        applied_date = (
            vacancy.applied_at.strftime("%d.%m.%Y %H:%M")
            if vacancy.applied_at
            else "не вказано"
        )

        await callback.message.answer(
            "📨 Резюме відправлено\n"
            f"{vacancy.title}\n"
            f"Дата: {applied_date}"
        )


@router.callback_query(
    VacancyActionCallback.filter(
        F.action == "interview",
    )
)
async def handle_interview_vacancy(
    callback: CallbackQuery,
    callback_data: VacancyActionCallback,
) -> None:
    vacancy = await vacancy_repository.set_status(
        vacancy_id=callback_data.vacancy_id,
        telegram_user_id=callback.from_user.id,
        status=VacancyStatus.INTERVIEW,
    )

    if vacancy is None:
        await callback.answer(
            "Вакансію не знайдено.",
            show_alert=True,
        )
        return

    await callback.answer("Статус змінено на «Співбесіда»")

    if callback.message:
        await callback.message.edit_reply_markup(
            reply_markup=None,
        )

        interview_date = (
            vacancy.interview_at.strftime("%d.%m.%Y %H:%M")
            if vacancy.interview_at
            else "не вказано"
        )

        await callback.message.answer(
            "🎤 Співбесіда\n"
            f"{vacancy.title}\n"
            f"Дата зміни статусу: {interview_date}"
        )