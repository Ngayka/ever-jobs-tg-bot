from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.database.repository.subscription_repository import subscription_repository
from app.keyboards.callbacks import SubscriptionCallback

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


        await subscription_repository.create_or_get(
            telegram_user_id=callback.from_user.id,
            search_term=search_term,
            source_group=source_group,
            location=location,
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

        await callback.answer(
            "Subscription disabled 🔕",
            show_alert=True,
        )
        return

    await callback.answer(
        "Unknown subscription action.",
        show_alert=True,
    )
