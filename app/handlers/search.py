from html import escape
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.models import VacancyStatus
from app.database.repository.vacancy_repository import vacancy_repository
from app.docs.job_sources import (
    get_enabled_sources, SourceGroup
)
from app.keyboards.callbacks import (
    SourceGroupCallback
)
from app.keyboards.main_menu import SEARCH_JOBS_BUTTON
from app.keyboards.search_filters import (
    build_source_keyboard,
)
from app.keyboards.vacancy_actions import (
    build_vacancy_actions_keyboard,
)
from app.services.ever_jobs_client import (
    EverJobsApiError,
    ever_jobs_client,
)
from app.services.job_relevance import (
    is_job_relevant,
)
from app.services.job_search import search_relevant_jobs
from app.states.search import SearchStates


router = Router()


@router.message(F.text == SEARCH_JOBS_BUTTON)
async def request_search_term(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Обробляє натискання кнопки «Знайти вакансії».

    Переводить користувача у стан очікування
    пошукового запиту.
    """
    await state.clear()
    await state.set_state(
        SearchStates.waiting_for_search_term
    )

    await message.answer(
        "What are you looking for?\n\n"
        "e.g.:\n"
        "• Python Developer\n"
        "• Junior Odoo Developer\n"
        "• Data Analyst"
    )
@router.message(
    SearchStates.waiting_for_search_term,
    F.text,
)
async def receive_search_term(
    message: Message,
    state: FSMContext,
) -> None:
    search_term = (message.text or "").strip()

    if not search_term:
        await message.answer(
            "Enter job title or speciality."
        )
        return

    await state.update_data(
        search_term=search_term,
    )

    await state.set_state(
        SearchStates.waiting_for_source_type
    )

    await message.answer(
        "Where should I search?",
        reply_markup=build_source_keyboard(),
    )

@router.callback_query(
    SearchStates.waiting_for_source_type,
    SourceGroupCallback.filter(),
)
async def select_source_type_and_search(
    callback: CallbackQuery,
    callback_data: SourceGroupCallback,
    state: FSMContext,
) -> None:
    try:
        source_group = SourceGroup(
            callback_data.source_group
        )
    except ValueError:
        await callback.answer(
            "Unknown source group.",
            show_alert=True,
        )
        return
    data = await state.get_data()

    search_term = str(
        data.get("search_term") or ""
    ).strip()

    if not search_term:
        await callback.answer(
            "Search data lost. Please start search again.",
            show_alert=True,
        )
        await state.clear()
        return
    sites = get_enabled_sources(
        group=source_group,
    )

    await state.update_data(
        source_group=source_group.value,
    )

    await callback.answer()

    if callback.message is None:
        return

    status_message = callback.message

    await status_message.edit_text(
        "🔎 Looking for vacancies\n\n"
        f"Title: <b>{escape(search_term)}</b>\n"
        f"Sources: <b>{escape(source_group.value)}</b>",
        parse_mode="HTML",
    )

    try:
        jobs = await search_relevant_jobs(
            search_term=search_term,
            source_group=source_group,
            results_wanted=10,
        )
    except EverJobsApiError as error:
        await status_message.edit_text(
            "Search failed.\n\n"
            f"<code>{escape(str(error))}</code>",
            parse_mode="HTML",
        )
        await state.clear()
        return

    if not jobs:
        await status_message.edit_text(
            f"No jobs found for "
            f"<b>{escape(search_term)}</b>",
            parse_mode="HTML",
        )
        await state.clear()
        return

    relevant_jobs = [
        job for job in jobs
        if is_job_relevant(
            job=job,
            search_term=search_term,
        )
    ]

    if not relevant_jobs:
        await status_message.edit_text(
            "Vacancies were found, but none matched "
            "the required skills closely enough."
        )
        await state.clear()
        return

    visible_jobs: list[dict[str, Any]] = []

    for job in relevant_jobs:
        site = str(job.get("site") or "unknown")
        external_job_id = str(
            job.get("id")
            or job.get("jobUrl")
            or ""
        )

        existing = (
            await vacancy_repository.get_by_external_id(
                telegram_user_id=callback.from_user.id,
                site=site,
                external_job_id=external_job_id,
            )
        )

        if (
            existing is not None
            and existing.status != VacancyStatus.NEW
        ):
            continue

        visible_jobs.append(job)

    if not visible_jobs:
        await status_message.edit_text(
            "No new vacancies.\n"
            "You have processed all of them."
        )
        await state.clear()
        return

    await state.set_state(
        SearchStates.browsing_results
    )

    await state.update_data(
        search_jobs=visible_jobs,
        current_job_index=0,
    )

    first_job = visible_jobs[0]

    vacancy = await vacancy_repository.create_or_get(
        telegram_user_id=callback.from_user.id,
        job=first_job,
    )

    await status_message.edit_text(
        format_job_card(
            first_job,
            current_index=0,
            total_jobs=len(visible_jobs),
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=build_vacancy_actions_keyboard(
            vacancy_id=vacancy.id,
            status=vacancy.status,
            current_index=0,
            total_jobs=len(visible_jobs),
        ),
    )

def format_job_card(
    job: dict,
    *,
    current_index: int,
    total_jobs: int,
) -> str:
    title = escape(
        str(job.get("title") or "Untitled Role")
    )

    company = escape(
        str(
            job.get("companyName")
            or "No company name"
        )
    )

    job_url = str(job.get("jobUrl") or "")
    site = escape(
        str(job.get("site") or "unknown")
    )

    date_posted = escape(
        str(
            job.get("datePosted")
            or "No posted date"
        )
    )

    location_data = job.get("location") or {}

    if not isinstance(location_data, dict):
        location_data = {}

    location = build_location(location_data)

    remote_text = (
        "Yes"
        if job.get("isRemote")
        else "No or not specified"
    )

    lines = [
        f"<b>Vacancy {current_index + 1} from {total_jobs}</b>",
        "",
        f"<b>{title}</b>",
        f"🏢 {company}",
        f"📍 {escape(location)}",
        f"🏠 Remote: {remote_text}",
        f"🌐 Website: {site}",
        f"📅 Date: {date_posted}",
    ]

    if job_url:
        safe_url = escape(
            job_url,
            quote=True,
        )

        lines.extend(
            [
                "",
                f'🔗 <a href="{safe_url}">'
                "View Vacancy"
                "</a>",
            ]
        )

    return "\n".join(lines)


def build_location(
    location: dict[str, Any],
) -> str:
    """
    Збирає місто, регіон і країну в один рядок.
    """
    parts = [
        location.get("city"),
        location.get("state"),
        location.get("country"),
    ]

    cleaned_parts = [
        str(part).strip()
        for part in parts
        if part
    ]

    return ", ".join(cleaned_parts) or "Not specified"
