from typing import Any
from app.docs.job_sources import SourceGroup, get_enabled_sources
from app.services.ever_jobs_client import ever_jobs_client
from app.services.job_relevance import is_job_relevant


async def search_relevant_jobs(
    *,
    search_term: str,
    source_group: SourceGroup,
    location: str | None = None,
    results_wanted: int = 10,
) -> list[dict[str, Any]]:
    sites = get_enabled_sources(group=source_group)

    jobs = await ever_jobs_client.search_jobs(
        search_term=search_term,
        sites=sites,
        location=location,
        results_wanted=results_wanted,
        dedup=True,
    )

    print(
        "SEARCH DEBUG:",
        "term=", search_term,
        "group=", source_group,
        "location=", location,
        "sites=", sites,
        "jobs_from_api=", len(jobs),
    )

    return jobs