import asyncio
from typing import Any
import httpx
from app.config import settings


SEARCH_JOBS_QUERY = """
query SearchJobs($input: SearchJobsInput!) {
  searchJobs(input: $input) {
    count
    rawCount
    cached
    jobs {
      id
      title
      companyName
      jobUrl
      isRemote
      datePosted
      site
      location {
        city
        state
        country
      }
    }
  }
}
"""


class EverJobsApiError(Exception):
    """Помилка під час звернення до Ever Jobs API."""


class EverJobsClient:
    def __init__(self, api_url: str) -> None:
        self.api_url = api_url

    @staticmethod
    def _deduplicate_jobs(
            jobs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        unique_jobs: list[dict[str, Any]] = []
        seen_keys: set[str] = set()

        for job in jobs:
            job_url = str(job.get("jobUrl") or "").strip()
            title = str(job.get("title") or "").strip().lower()
            company = str(
                job.get("companyName") or ""
            ).strip().lower()

            # Спочатку дедуплікуємо за URL.
            # Якщо URL немає — за title + company.
            key = job_url or f"{title}|{company}"

            if not key or key in seen_keys:
                continue

            seen_keys.add(key)
            unique_jobs.append(job)

        return unique_jobs


    async def search_jobs(
        self,
        search_term: str,
        *,
        results_wanted: int = 5,
        sites: list[str] | None = None,
        dedup: bool = True,
    ) -> list[dict[str, Any]]:
        input_data: dict[str, Any] = {
            "searchTerm": search_term,
            "resultsWanted": results_wanted,
            "dedup": dedup,
        }

        if sites:
            input_data["siteType"] = sites

        payload = {
            "query": SEARCH_JOBS_QUERY,
            "variables": {
                "input": input_data,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.TimeoutException as error:
            raise EverJobsApiError(
                "Ever Jobs API не відповів вчасно."
            ) from error
        except httpx.HTTPError as error:
            raise EverJobsApiError(
                f"Не вдалося звернутися до Ever Jobs API: {error}"
            ) from error

        data = response.json()

        if data.get("errors"):
            message = data["errors"][0].get(
                "message",
                "Невідома GraphQL-помилка",
            )
            raise EverJobsApiError(message)

        search_result = (
            data
            .get("data", {})
            .get("searchJobs")
        )

        if not search_result:
            raise EverJobsApiError(
                "API повернув відповідь без searchJobs."
            )

        jobs = search_result.get("jobs", [])

        if not isinstance(jobs, list):
            raise EverJobsApiError(
                "API повернув вакансії у неправильному форматі."
            )

        return jobs


ever_jobs_client = EverJobsClient(
    api_url=settings.ever_jobs_api_url,
)