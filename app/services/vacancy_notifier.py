from app.database.models import JobSubscription
from app.database.repository import vacancy_repository
from app.docs.job_sources import SourceGroup, get_enabled_sources
from app.services.job_search import search_relevant_jobs


async def check_subscription(
    subscription: JobSubscription,
) -> list[dict]:

    relevant_jobs = await search_relevant_jobs(
        search_term=subscription.search_term,
        source_group=SourceGroup(
            subscription.source_group
        ),
        results_wanted=20,
    )

    new_jobs = []

    for job in relevant_jobs:
        site = str(job.get("site") or "unknown")

        external_job_id = str(
            job.get("id")
            or job.get("jobUrl")
            or ""
        )

        existing = (
            await vacancy_repository.get_by_external_id(
                telegram_user_id=subscription.telegram_user_id,
                site=site,
                external_job_id=external_job_id,
            )
        )

        if existing is not None:
            continue

        new_jobs.append(job)

    return new_jobs