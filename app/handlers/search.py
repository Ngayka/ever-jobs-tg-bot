from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.job_sources import SourceGroup

from app.services.ever_jobs_client import (
    EverJobsApiError,
    ever_jobs_client,
)

router = Router()

@router.message(Command("search"))
async def handle_search(message: Message) -> None:
    search_term = extract_search_term(message.text)

    if not search_term:
        await message.answer(
            "Вкажіть, яку вакансію потрібно знайти.\n\n"
            "Наприклад:\n"
            "<code>/search python developer</code>",
            parse_mode="HTML",
        )
        return

    status_message = await message.answer(
        f"🔎 Шукаю вакансії за запитом: "
        f"<b>{escape(search_term)}</b>...",
        parse_mode="HTML",
    )

    try:
        jobs = await ever_jobs_client.search_groups(
            search_term=search_term,
            groups=[
                SourceGroup.UKRAINE,
                #SourceGroup.GLOBAL,
                #SourceGroup.COMPANIES,
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

    await status_message.edit_text(
        f"Знайдено вакансій: <b>{len(jobs)}</b>",
        parse_mode="HTML",
    )

    for job in jobs:
        await message.answer(
            format_job(job),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


def extract_search_term(text: str | None) -> str | None:
    if not text:
        return None

    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        return None

    search_term = parts[1].strip()

    return search_term or None


def format_job(job: dict) -> str:
    title = escape(job.get("title") or "Без назви")
    company = escape(
        job.get("companyName") or "Компанію не вказано"
    )
    job_url = job.get("jobUrl") or ""
    site = escape(job.get("site") or "unknown")
    date_posted = escape(
        job.get("datePosted") or "дату не вказано"
    )

    location_data = job.get("location") or {}
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
            f'🔗 <a href="{safe_url}">Відкрити вакансію</a>'
        )

    return "\n".join(lines)


def build_location(location: dict) -> str:
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
