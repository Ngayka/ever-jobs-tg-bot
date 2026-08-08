from app.docs.job_sources import SourceGroup, get_enabled_sources
from app.services.ever_jobs_client import ever_jobs_client
from app.services.job_relevance import is_job_relevant


async def search_relevant_jobs(
    *,
    search_term: str,
    source_group: SourceGroup,
    results_wanted: int = 10,
) -> list[dict]:
    sites = get_enabled_sources(
        group=source_group,
    )

    jobs = await ever_jobs_client.search_jobs(
        search_term=search_term,
        sites=sites,
        results_wanted=results_wanted,
        dedup=True,
    )

    return [
        job
        for job in jobs
        if is_job_relevant(
            job=job,
            search_term=search_term,
        )
    ]