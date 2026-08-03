from html import escape
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.models import VacancyStatus
from app.database.repository import vacancy_repository
from app.job_sources import SourceGroup
from app.keyboards.main_menu import SEARCH_JOBS_BUTTON
from app.keyboards.vacancy_actions import (
    build_vacancy_actions_keyboard,
)
from app.services.ever_jobs_client import (
    EverJobsApiError,
    ever_jobs_client,
)
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
    await state.set_state(
        SearchStates.waiting_for_search_term
    )

    await message.answer(
        "Що шукаємо?\n\n"
        "Наприклад:\n"
        "• Python Developer\n"
        "• Junior Odoo Developer\n"
        "• Data Analyst"
    )


@router.message(
    SearchStates.waiting_for_search_term,
    F.text,
)
async def handle_search(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Отримує пошуковий запит користувача,
    викликає Ever Jobs API та показує нові вакансії.
    """
    search_term = (message.text or "").strip()

    if not search_term:
        await message.answer(
            "Напишіть назву вакансії або спеціальності."
        )
        return

    # Завершуємо режим очікування пошукового запиту.
    await state.clear()

    status_message = await message.answer(
        "🔎 Шукаю вакансії за запитом: "
        f"<b>{escape(search_term)}</b>...",
        parse_mode="HTML",
    )

    try:
        jobs = await ever_jobs_client.search_groups(
            search_term=search_term,
            groups=[
                SourceGroup.UKRAINE,
                # SourceGroup.GLOBAL,
                # SourceGroup.COMPANIES,
            ],
            results_per_source=5,
        )
    except EverJobsApiError as error:
        await status_message.edit_text(
            "Не вдалося виконати пошук.\n\n"
            f"<code>{escape(str(error))}</code>",
            parse_mode="HTML",
        )
        return

    if not jobs:
        await status_message.edit_text(
            f"За запитом <b>{escape(search_term)}</b> "
            "вакансій не знайдено.",
            parse_mode="HTML",
        )
        return

    if message.from_user is None:
        await status_message.edit_text(
            "Не вдалося визначити користувача Telegram."
        )
        return

    new_jobs_count = 0

    for job in jobs:
        vacancy = await vacancy_repository.create_or_get(
            telegram_user_id=message.from_user.id,
            job=job,
        )

        # Відхилені, applied, interview та інші
        # оброблені вакансії повторно не показуємо.
        if vacancy.status != VacancyStatus.NEW:
            continue

        new_jobs_count += 1

        await message.answer(
            format_job(job),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=build_vacancy_actions_keyboard(
                vacancy_id=vacancy.id,
                status=vacancy.status,
            ),
        )

    if new_jobs_count == 0:
        await status_message.edit_text(
            "Нових вакансій немає.\n"
            "Усі знайдені вакансії ви вже переглядали."
        )
        return

    await status_message.edit_text(
        "Знайдено нових вакансій: "
        f"<b>{new_jobs_count}</b>",
        parse_mode="HTML",
    )


def format_job(job: dict[str, Any]) -> str:
    """
    Форматує одну вакансію для Telegram.
    """
    title = escape(
        str(job.get("title") or "Без назви")
    )

    company = escape(
        str(
            job.get("companyName")
            or "Компанію не вказано"
        )
    )

    job_url = str(job.get("jobUrl") or "")
    site = escape(str(job.get("site") or "unknown"))

    date_posted = escape(
        str(
            job.get("datePosted")
            or "дату не вказано"
        )
    )

    location_data = job.get("location") or {}

    if not isinstance(location_data, dict):
        location_data = {}

    location = build_location(location_data)

    remote_text = (
        "Так"
        if job.get("isRemote")
        else "Ні або не вказано"
    )

    lines = [
        f"<b>{title}</b>",
        f"🏢 {company}",
        f"📍 {escape(location)}",
        f"🏠 Remote: {remote_text}",
        f"🌐 Джерело: {site}",
        f"📅 Дата: {date_posted}",
    ]

    if job_url:
        safe_url = escape(job_url, quote=True)

        lines.append(
            f'🔗 <a href="{safe_url}">'
            "Відкрити вакансію"
            "</a>"
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

    return ", ".join(cleaned_parts) or "Не вказано"