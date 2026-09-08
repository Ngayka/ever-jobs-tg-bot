from aiogram.types import InlineKeyboardButton

from app.keyboards.callbacks import SubscriptionCallback


def unsubscribe_button(subscription_id: int) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="🔕 Unsubscribe",
        callback_data=SubscriptionCallback(
            action="unsubscribe",
            subscription_id=subscription_id,
        ).pack(),
    )
