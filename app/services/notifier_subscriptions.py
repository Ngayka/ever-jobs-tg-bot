import logging

from aiogram import Bot

from app.database.models import JobSubscription
from app.database.repository.vacancy_repository import vacancy_repository
from app.handlers.search import format_job_card
from app.keyboards.vacancy_actions import build_vacancy_actions_keyboard
from app.services.vacancy_notifier import check_subscription

logger = logging.getLogger(__name__)

async def notify_subscription(
    bot: Bot,
    subscription: JobSubscription,
) -> None:
    jobs = await check_subscription(
        subscription
    )

    logger.info(
        "Subscription id=%s: found %s new jobs",
        subscription.id,
        len(jobs),
    )

    for job in jobs:
        vacancy = (
            await vacancy_repository.create_or_get(
                telegram_user_id=subscription.telegram_user_id,
                job=job,
            )
        )

        await bot.send_message(
            chat_id=subscription.telegram_user_id,
            text=(
                "🆕 <b>New vacancy</b>\n\n"
                + format_job_card(
                    job,
                    current_index=0,
                    total_jobs=1,
                )
            ),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=build_vacancy_actions_keyboard(
                vacancy_id=vacancy.id,
                status=vacancy.status,
                current_index=0,
                total_jobs=1,
            ),
        )