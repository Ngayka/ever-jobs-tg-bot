from unittest.mock import AsyncMock, patch

import pytest

from app.docs.job_sources import SourceGroup
from app.services.job_search import search_relevant_jobs


@pytest.fixture
def jobs():
    return [
        {"id": "python-1", "title": "Python Developer"},
        {"id": "sales-1", "title": "Sales Manager"},
    ]


@pytest.mark.asyncio
async def test_search_uses_sources_for_requested_group(jobs):
    sources = ["DOU", "DJINNI"]

    with (
        patch(
            "app.services.job_search.get_enabled_sources",
            return_value=sources,
        ) as get_enabled_sources,
        patch(
            "app.services.job_search.ever_jobs_client.search_jobs",
            new_callable=AsyncMock,
            return_value=jobs,
        ),
        patch(
            "app.services.job_search.is_job_relevant",
            return_value=True,
        ),
    ):
        await search_relevant_jobs(
            search_term="python",
            source_group=SourceGroup.UKRAINE,
        )

    get_enabled_sources.assert_called_once_with(group=SourceGroup.UKRAINE)


@pytest.mark.asyncio
async def test_search_calls_client_with_expected_parameters(jobs):
    search_jobs = AsyncMock(return_value=jobs)

    with (
        patch(
            "app.services.job_search.get_enabled_sources",
            return_value=["DOU"],
        ),
        patch(
            "app.services.job_search.ever_jobs_client.search_jobs",
            search_jobs,
        ),
        patch(
            "app.services.job_search.is_job_relevant",
            return_value=True,
        ),
    ):
        await search_relevant_jobs(
            search_term="python developer",
            source_group=SourceGroup.UKRAINE,
            results_wanted=25,
        )

    search_jobs.assert_awaited_once_with(
        search_term="python developer",
        sites=["DOU"],
        results_wanted=25,
        dedup=True,
    )


@pytest.mark.asyncio
async def test_search_returns_only_relevant_jobs(jobs):
    with (
        patch(
            "app.services.job_search.get_enabled_sources",
            return_value=["DOU"],
        ),
        patch(
            "app.services.job_search.ever_jobs_client.search_jobs",
            new_callable=AsyncMock,
            return_value=jobs,
        ),
        patch(
            "app.services.job_search.is_job_relevant",
            side_effect=lambda *, job, search_term: job["id"] == "python-1",
        ) as is_job_relevant,
    ):
        result = await search_relevant_jobs(
            search_term="python",
            source_group=SourceGroup.UKRAINE,
        )

    assert result == [jobs[0]]
    assert is_job_relevant.call_count == 2


@pytest.mark.asyncio
async def test_search_returns_empty_list_for_empty_api_response():
    with (
        patch(
            "app.services.job_search.get_enabled_sources",
            return_value=["DOU"],
        ),
        patch(
            "app.services.job_search.ever_jobs_client.search_jobs",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch("app.services.job_search.is_job_relevant") as is_job_relevant,
    ):
        result = await search_relevant_jobs(
            search_term="python",
            source_group=SourceGroup.UKRAINE,
        )

    assert result == []
    is_job_relevant.assert_not_called()
