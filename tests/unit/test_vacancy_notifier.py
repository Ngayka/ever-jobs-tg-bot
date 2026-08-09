from types import SimpleNamespace
from unittest.mock import AsyncMock, call, patch

import pytest

from app.docs.job_sources import SourceGroup
from app.services.vacancy_notifier import check_subscription


@pytest.fixture
def subscription():
    return SimpleNamespace(
        id=10,
        telegram_user_id=12345,
        search_term="python developer",
        source_group=SourceGroup.UKRAINE.value,
        enabled=True,
    )


@pytest.fixture
def jobs():
    return [
        {"id": "dou-1", "site": "DOU", "title": "Python Developer"},
        {"id": "djinni-2", "site": "DJINNI", "title": "Backend Developer"},
    ]


@pytest.mark.asyncio
async def test_check_subscription_returns_only_previously_unseen_jobs(
    subscription, jobs
):
    get_by_external_id = AsyncMock(side_effect=[object(), None])

    with (
        patch(
            "app.services.vacancy_notifier.search_relevant_jobs",
            new_callable=AsyncMock,
            return_value=jobs,
        ) as search_jobs,
        patch(
            "app.services.vacancy_notifier.vacancy_repository.get_by_external_id",
            get_by_external_id,
        ),
    ):
        result = await check_subscription(subscription)

    assert result == [jobs[1]]
    search_jobs.assert_awaited_once_with(
        search_term="python developer",
        source_group=SourceGroup.UKRAINE,
        results_wanted=20,
    )
    assert get_by_external_id.await_args_list == [
        call(telegram_user_id=12345, site="DOU", external_job_id="dou-1"),
        call(
            telegram_user_id=12345,
            site="DJINNI",
            external_job_id="djinni-2",
        ),
    ]


@pytest.mark.asyncio
async def test_check_subscription_ignores_all_stored_jobs(subscription, jobs):
    with (
        patch(
            "app.services.vacancy_notifier.search_relevant_jobs",
            new_callable=AsyncMock,
            return_value=jobs,
        ),
        patch(
            "app.services.vacancy_notifier.vacancy_repository.get_by_external_id",
            new_callable=AsyncMock,
            side_effect=[object(), object()],
        ),
    ):
        assert await check_subscription(subscription) == []


@pytest.mark.asyncio
async def test_check_subscription_returns_multiple_new_jobs(subscription, jobs):
    with (
        patch(
            "app.services.vacancy_notifier.search_relevant_jobs",
            new_callable=AsyncMock,
            return_value=jobs,
        ),
        patch(
            "app.services.vacancy_notifier.vacancy_repository.get_by_external_id",
            new_callable=AsyncMock,
            return_value=None,
        ),
    ):
        assert await check_subscription(subscription) == jobs


@pytest.mark.asyncio
async def test_check_subscription_returns_empty_list_for_empty_search(
    subscription,
):
    get_by_external_id = AsyncMock()

    with (
        patch(
            "app.services.vacancy_notifier.search_relevant_jobs",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "app.services.vacancy_notifier.vacancy_repository.get_by_external_id",
            get_by_external_id,
        ),
    ):
        assert await check_subscription(subscription) == []

    get_by_external_id.assert_not_awaited()
