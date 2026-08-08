import asyncio
import logging

from aiogram import Bot

from app.database.repository.subscription_repository import subscription_repository
from app.services.notifier_subscriptions import notify_subscription


logger = logging.getLogger(__name__)

async def subscription_worker(
    bot: Bot,
) -> None:
    while True:
        try:
            subscriptions = (
                await subscription_repository.get_enabled()
            )

            for subscription in subscriptions:
                await notify_subscription(
                    bot,
                    subscription,
                )

        except Exception:
            logger.exception(
                "Subscription worker failed"
            )

        await asyncio.sleep(3600)