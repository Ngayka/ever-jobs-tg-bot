from aiogram.types import InlineKeyboardButton

from app.keyboards.callbacks import SubscriptionCallback


InlineKeyboardButton(
    text="🔕 Unsubscribe",
    callback_data=SubscriptionCallback(
        action="unsubscribe",
    ).pack(),
)