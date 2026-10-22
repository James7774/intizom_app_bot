"""Inline keyboards for Intizom Bot."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_task_confirmation_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Renders simple confirmation buttons for a selected task:
    [ ✅ Bajardim ]  [ ❌ Bajarmadim ]
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Bajardim",
                callback_data=f"ans:{task_id}:done",
            ),
            InlineKeyboardButton(
                text="❌ Bajarmadim",
                callback_data=f"ans:{task_id}:missed",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_stats_keyboard() -> InlineKeyboardMarkup:
    """Returns interactive inline buttons for the statistics view."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Yangilash",
                    callback_data="stats:refresh",
                ),
                InlineKeyboardButton(
                    text="✅ Chek-listga o‘tish",
                    callback_data="stats:to_checklist",
                ),
            ]
        ]
    )
