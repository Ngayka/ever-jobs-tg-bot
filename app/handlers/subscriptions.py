from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.repository.subscription_repository import subscription_repository
from app.database.repository.vacancy_repository import vacancy_repository
from app.keyboards.callbacks import SubscriptionCallback
from app.keyboards.vacancy_actions import build_vacancy_actions_keyboard

router = Router()


@router.callback_query(
    SubscriptionCallback.filter(),
)
async def subscription_action(
    callback: CallbackQuery,
    callback_data: SubscriptionCallback,
    state: FSMContext,
):
    if callback_data.action == "subscribe":
        data = await state.get_data()

        search_term = str(
            data.get("search_term") or ""
        ).strip()

        source_group = str(
            data.get("source_group") or ""
        ).strip()

        location = data.get("location")

        if not search_term or not source_group:
            await callback.answer(
                "Search data lost.",
                show_alert=True,
            )
            return


        subscription = await subscription_repository.create_or_get(
            telegram_user_id=callback.from_user.id,
            search_term=search_term,
            source_group=source_group,
            location=location,
        )
        jobs = data.get("search_jobs", [])
        current_index = data.get("current_job_index", 0)

        if jobs and isinstance(callback.message, Message):
            job = jobs[current_index]

            vacancy = await vacancy_repository.create_or_get(
                telegram_user_id=callback.from_user.id,
                job=job,
            )

            await callback.message.edit_reply_markup(
                reply_markup=build_vacancy_actions_keyboard(
                    vacancy_id=vacancy.id,
                    status=vacancy.status,
                    current_index=current_index,
                    total_jobs=len(jobs),
                    subscription_id=subscription.id,
                )
            )

        await callback.answer(
            "Subscription enabled ✅",
            show_alert=True,
        )
        return

    elif callback_data.action == "unsubscribe":
        if callback_data.subscription_id is None:
            await callback.answer(
                "Subscription not found.",
                show_alert=True,
            )
            return

        disabled = await subscription_repository.disable(
            subscription_id=callback_data.subscription_id,
            telegram_user_id=callback.from_user.id,
        )

        if not disabled:
            await callback.answer(
                "Subscription not found.",
                show_alert=True,
            )
            return
        data = await state.get_data()
        jobs = data.get("search_jobs", [])
        current_index = data.get("current_job_index", 0)

        if jobs and isinstance(callback.message, Message):
            job = jobs[current_index]

            vacancy = await vacancy_repository.create_or_get(
                telegram_user_id=callback.from_user.id,
                job=job,
            )

            await callback.message.edit_reply_markup(
                reply_markup=build_vacancy_actions_keyboard(
                    vacancy_id=vacancy.id,
                    status=vacancy.status,
                    current_index=current_index,
                    total_jobs=len(jobs),
                    subscription_id=None,
                )
            )

        await callback.answer(
            "Subscription disabled 🔕",
            show_alert=True,
        )
        return

    await callback.answer(
        "Unknown subscription action.",
        show_alert=True,
    )
