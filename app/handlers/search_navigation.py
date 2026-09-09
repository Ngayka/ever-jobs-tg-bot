from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.database.repository.subscription_repository import subscription_repository
from app.database.repository.vacancy_repository import vacancy_repository
from app.handlers.search import format_job_card
from app.keyboards.callbacks import SearchNavigationCallback
from app.keyboards.vacancy_actions import (
    build_vacancy_actions_keyboard,
)
from app.states.search import SearchStates


router = Router()


@router.callback_query(
    SearchStates.browsing_results,
    SearchNavigationCallback.filter(
        F.action.in_({"previous", "next"}),
    ),
)
async def navigate_search_results(
    callback: CallbackQuery,
    callback_data: SearchNavigationCallback,
    state: FSMContext,
) -> None:
    data = await state.get_data()

    jobs = data.get("search_jobs", [])
    current_index = data.get(
        "current_job_index",
        0,
    )

    if not jobs:
        await callback.answer(
            "Results no longer available.",
            show_alert=True,
        )
        return

    if callback_data.action == "next":
        new_index = min(
            current_index + 1,
            len(jobs) - 1,
        )
    else:
        new_index = max(
            current_index - 1,
            0,
        )

    job = jobs[new_index]

    vacancy = await vacancy_repository.create_or_get(
        telegram_user_id=callback.from_user.id,
        job=job,
    )

    subscription = await subscription_repository.get_active_for_search(
        telegram_user_id=callback.from_user.id,
        search_term=str(data.get("search_term") or "").strip(),
        source_group=str(data.get("source_group") or "").strip(),
        location=data.get("location"),
    )

    await state.update_data(
        current_job_index=new_index,
    )

    await callback.answer()

    if callback.message is None:
        return

    await callback.message.edit_text(
        format_job_card(
            job,
            current_index=new_index,
            total_jobs=len(jobs),
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=build_vacancy_actions_keyboard(
            vacancy_id=vacancy.id,
            status=vacancy.status,
            current_index=new_index,
            total_jobs=len(jobs),
            subscription_id=(
                subscription.id
                if subscription is not None
                else None
            )
        ),
    )


@router.callback_query(
    SearchNavigationCallback.filter(
        F.action == "current",
    ),
)
async def handle_current_page_button(
    callback: CallbackQuery,
) -> None:
    await callback.answer(
        "Current vacancy number."
    )
