import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from app.services.subscription import subscription_worker


@pytest.fixture
def subscriptions():
    return [
        SimpleNamespace(id=1, enabled=True),
        SimpleNamespace(id=2, enabled=True),
    ]


@pytest.mark.asyncio
async def test_worker_loads_active_subscriptions_and_notifies_each(subscriptions):
    bot = MagicMock()
    get_enabled = AsyncMock(return_value=subscriptions)
    notify = AsyncMock()

    with (
        patch(
            "app.services.subscription.subscription_repository.get_enabled",
            get_enabled,
        ),
        patch("app.services.subscription.notify_subscription", notify),
        patch(
            "app.services.subscription.asyncio.sleep",
            new_callable=AsyncMock,
            side_effect=asyncio.CancelledError,
        ) as sleep,
    ):
        with pytest.raises(asyncio.CancelledError):
            await subscription_worker(bot)

    get_enabled.assert_awaited_once_with()
    assert notify.await_args_list == [
        call(bot, subscriptions[0]),
        call(bot, subscriptions[1]),
    ]
    sleep.assert_awaited_once_with(3600)


@pytest.mark.asyncio
async def test_worker_logs_iteration_error_and_continues(caplog):
    bot = MagicMock()
    subscription = SimpleNamespace(id=1, enabled=True)
    get_enabled = AsyncMock(return_value=[subscription])
    notify = AsyncMock(side_effect=[RuntimeError("temporary failure"), None])
    sleep = AsyncMock(side_effect=[None, asyncio.CancelledError])

    with (
        patch(
            "app.services.subscription.subscription_repository.get_enabled",
            get_enabled,
        ),
        patch("app.services.subscription.notify_subscription", notify),
        patch("app.services.subscription.asyncio.sleep", sleep),
        caplog.at_level("ERROR", logger="app.services.subscription"),
    ):
        with pytest.raises(asyncio.CancelledError):
            await subscription_worker(bot)

    assert "Subscription worker failed" in caplog.text
    assert "temporary failure" in caplog.text
    assert get_enabled.await_count == 2
    assert notify.await_count == 2
    assert sleep.await_args_list == [call(3600), call(3600)]
