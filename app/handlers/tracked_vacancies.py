from html import escape

from aiogram import F, Router
from aiogram.types import Message

from app.database.models import (
    TrackedVacancy,
    VacancyStatus,
)
from app.database.repository.vacancy_repository import vacancy_repository
from app.keyboards.main_menu import (
    APPLIED_JOBS_BUTTON,
    INTERVIEWS_BUTTON,
)
from app.keyboards.vacancy_actions import (
    build_vacancy_actions_keyboard,
)


router = Router()


@router.message(F.text == APPLIED_JOBS_BUTTON)
async def show_applied_vacancies(
    message: Message,
) -> None:
    if message.from_user is None:
        return

    vacancies = await vacancy_repository.get_by_status(
        telegram_user_id=message.from_user.id,
        status=VacancyStatus.APPLIED,
    )

    if not vacancies:
        await message.answer(
            "У папці «Відправлені резюме» "
            "поки немає вакансій."
        )
        return

    await message.answer(
        f"📨 Відправлені резюме: {len(vacancies)}"
    )

    for vacancy in vacancies:
        await message.answer(
            format_tracked_vacancy(vacancy),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=build_vacancy_actions_keyboard(
                vacancy_id=vacancy.id,
                status=vacancy.status,
            ),
        )


@router.message(F.text == INTERVIEWS_BUTTON)
async def show_interview_vacancies(
    message: Message,
) -> None:
    if message.from_user is None:
        return

    vacancies = await vacancy_repository.get_by_status(
        telegram_user_id=message.from_user.id,
        status=VacancyStatus.INTERVIEW,
    )

    if not vacancies:
        await message.answer(
            "У папці «Співбесіди» "
            "поки немає вакансій."
        )
        return

    await message.answer(
        f"🎤 Співбесіди: {len(vacancies)}"
    )

    for vacancy in vacancies:
        await message.answer(
            format_tracked_vacancy(vacancy),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


def format_tracked_vacancy(
    vacancy: TrackedVacancy,
) -> str:
    title = escape(vacancy.title)
    company = escape(
        vacancy.company_name
        or "Компанію не вказано"
    )
    location = escape(
        vacancy.location or "Не вказано"
    )
    site = escape(vacancy.site)

    lines = [
        f"<b>{title}</b>",
        f"🏢 {company}",
        f"📍 {location}",
        f"🌐 Джерело: {site}",
    ]

    if vacancy.status == VacancyStatus.APPLIED:
        applied_at = (
            vacancy.applied_at.strftime(
                "%d.%m.%Y %H:%M"
            )
            if vacancy.applied_at
            else "дату не вказано"
        )

        lines.append(
            f"📨 Резюме відправлено: {applied_at}"
        )

    if vacancy.status == VacancyStatus.INTERVIEW:
        interview_at = (
            vacancy.interview_at.strftime(
                "%d.%m.%Y %H:%M"
            )
            if vacancy.interview_at
            else "дату не вказано"
        )

        lines.append(
            f"🎤 Співбесіда: {interview_at}"
        )

    if vacancy.job_url:
        safe_url = escape(
            vacancy.job_url,
            quote=True,
        )
        lines.append(
            f'🔗 <a href="{safe_url}">'
            "Відкрити вакансію"
            "</a>"
        )

    return "\n".join(lines)
