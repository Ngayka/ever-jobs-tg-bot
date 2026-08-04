from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

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
    state: FSMContext,
) -> None:
    vacancy = await vacancy_repository.set_status(
        vacancy_id=callback_data.vacancy_id,
        telegram_user_id=callback.from_user.id,
        status=VacancyStatus.REJECTED,
    )

    if vacancy is None:
        await callback.answer(
            "Vacancy not found.",
            show_alert=True,
        )
        return

    await callback.answer("Vacancy rejected")

    if callback.message:
        data = await state.get_data()

        jobs = data.get("search_jobs", [])
        current_index = data.get(
            "current_job_index",
            0,
        )

        await callback.message.edit_reply_markup(
            reply_markup=build_vacancy_actions_keyboard(
                vacancy_id=vacancy.id,
                status=vacancy.status,
                current_index=current_index,
                total_jobs=len(jobs),
            ),
        )

        await callback.message.answer(
            f"❌ Reject: {vacancy.title}"
        )


@router.callback_query(
    VacancyActionCallback.filter(
        F.action == "applied",
    )
)
async def handle_applied_vacancy(
    callback: CallbackQuery,
    callback_data: VacancyActionCallback,
    state: FSMContext,
) -> None:
    vacancy = await vacancy_repository.set_status(
        vacancy_id=callback_data.vacancy_id,
        telegram_user_id=callback.from_user.id,
        status=VacancyStatus.APPLIED,
    )

    if vacancy is None:
        await callback.answer(
            "Vacancy not found.",
            show_alert=True,
        )
        return

    await callback.answer("Save in 'Sent CV's'")

    if callback.message:
        data = await state.get_data()

        jobs = data.get("search_jobs", [])
        current_index = data.get(
            "current_job_index",
            0,
        )

        await callback.message.edit_reply_markup(
            reply_markup=build_vacancy_actions_keyboard(
                vacancy_id=vacancy.id,
                status=vacancy.status,
                current_index=current_index,
                total_jobs=len(jobs),
            ),
        )

        applied_date = (
            vacancy.applied_at.strftime("%d.%m.%Y %H:%M")
            if vacancy.applied_at
            else "Not specified"
        )

        await callback.message.answer(
            "📨 Application submitted\n"
            f"{vacancy.title}\n"
            f"Date: {applied_date}"
        )


@router.callback_query(
    VacancyActionCallback.filter(
        F.action == "interview",
    )
)
async def handle_interview_vacancy(
    callback: CallbackQuery,
    callback_data: VacancyActionCallback,
    state: FSMContext,
) -> None:
    vacancy = await vacancy_repository.set_status(
        vacancy_id=callback_data.vacancy_id,
        telegram_user_id=callback.from_user.id,
        status=VacancyStatus.INTERVIEW,
    )

    if vacancy is None:
        await callback.answer(
            "Vacancy not found.",
            show_alert=True,
        )
        return

    await callback.answer("Status: Job's interview")

    if callback.message:
        data = await state.get_data()

        jobs = data.get("search_jobs", [])
        current_index = data.get(
            "current_job_index",
            0,
        )

        await callback.message.edit_reply_markup(
            reply_markup=build_vacancy_actions_keyboard(
                vacancy_id=vacancy.id,
                status=vacancy.status,
                current_index=current_index,
                total_jobs=len(jobs),
            ),
        )

        interview_date = (
            vacancy.interview_at.strftime("%d.%m.%Y %H:%M")
            if vacancy.interview_at
            else "Not specified"
        )

        await callback.message.answer(
            "🎤 Job Interview\n"
            f"{vacancy.title}\n"
            f"Date update: {interview_date}"
        )