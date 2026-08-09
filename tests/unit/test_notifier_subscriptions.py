from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from app.database.models import VacancyStatus
from app.services.notifier_subscriptions import notify_subscription


@pytest.fixture
def subscription():
    return SimpleNamespace(id=10, telegram_user_id=12345)


@pytest.fixture
def jobs():
    return [
        {"id": "dou-1", "site": "DOU", "title": "Python Developer"},
        {"id": "dou-2", "site": "DOU", "title": "Backend Developer"},
    ]


@pytest.mark.asyncio
async def test_notify_sends_each_new_job_with_html_and_keyboard(
    subscription, jobs
):
    bot = MagicMock()
    bot.send_message = AsyncMock()
    vacancies = [
        SimpleNamespace(id=101, status=VacancyStatus.NEW),
        SimpleNamespace(id=102, status=VacancyStatus.NEW),
    ]
    create_or_get = AsyncMock(side_effect=vacancies)
    keyboards = [MagicMock(name="first_keyboard"), MagicMock(name="second_keyboard")]

    with (
        patch(
            "app.services.notifier_subscriptions.check_subscription",
            new_callable=AsyncMock,
            return_value=jobs,
        ),
        patch(
            "app.services.notifier_subscriptions.vacancy_repository.create_or_get",
            create_or_get,
        ),
        patch(
            "app.services.notifier_subscriptions.build_vacancy_actions_keyboard",
            side_effect=keyboards,
        ) as build_keyboard,
        patch(
            "app.services.notifier_subscriptions.format_job_card",
            side_effect=["first card", "second card"],
        ),
    ):
        await notify_subscription(bot, subscription)

    assert create_or_get.await_args_list == [
        call(telegram_user_id=12345, job=jobs[0]),
        call(telegram_user_id=12345, job=jobs[1]),
    ]
    assert bot.send_message.await_count == 2
    for index, awaited_call in enumerate(bot.send_message.await_args_list):
        assert awaited_call.kwargs["chat_id"] == 12345
        assert awaited_call.kwargs["parse_mode"] == "HTML"
        assert awaited_call.kwargs["disable_web_page_preview"] is True
        assert awaited_call.kwargs["reply_markup"] is keyboards[index]
    assert build_keyboard.call_args_list == [
        call(
            vacancy_id=101,
            status=VacancyStatus.NEW,
            current_index=0,
            total_jobs=1,
        ),
        call(
            vacancy_id=102,
            status=VacancyStatus.NEW,
            current_index=0,
            total_jobs=1,
        ),
    ]


@pytest.mark.asyncio
async def test_notify_sends_nothing_when_there_are_no_new_jobs(subscription):
    bot = MagicMock()
    bot.send_message = AsyncMock()
    create_or_get = AsyncMock()

    with (
        patch(
            "app.services.notifier_subscriptions.check_subscription",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "app.services.notifier_subscriptions.vacancy_repository.create_or_get",
            create_or_get,
        ),
    ):
        await notify_subscription(bot, subscription)

    create_or_get.assert_not_awaited()
    bot.send_message.assert_not_awaited()
