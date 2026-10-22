"""Reply keyboards for Intizom Bot."""

from typing import List, Dict, Any
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Button labels constants
BTN_SETUP_TASKS = "📝 Topshiriqlarni kiritish"
BTN_CHECKLIST = "✅ Kunlik Intizom Chek-list"
BTN_STATS = "📊 Statistikam"
BTN_CANCEL = "🔙 Bekor qilish"
BTN_BACK_MAIN = "🔙 Asosiy menyu"


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Returns the primary navigation reply keyboard."""
    keyboard = [
        [KeyboardButton(text=BTN_SETUP_TASKS)],
        [KeyboardButton(text=BTN_CHECKLIST)],
        [KeyboardButton(text=BTN_STATS)],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Quyidagi menyudan tanlang...",
    )


def get_checklist_reply_keyboard(
    tasks: List[Dict[str, Any]], logs: Dict[int, str]
) -> ReplyKeyboardMarkup:
    """
    Renders user's daily tasks as reply keyboard buttons (in place of normal keyboard).
    Each task displays status emoji:
    - ✅ if completed
    - ❌ if missed
    - ⬜ if pending
    """
    keyboard: List[List[KeyboardButton]] = []
    current_row: List[KeyboardButton] = []

    for task in tasks:
        task_id = task["id"]
        task_name = task["task_name"]
        status = logs.get(task_id)

        if status == "done":
            icon = "✅"
        elif status == "missed":
            icon = "❌"
        else:
            icon = "⬜"

        button_text = f"{icon} {task_name}"
        current_row.append(KeyboardButton(text=button_text))

        if len(current_row) == 2:
            keyboard.append(current_row)
            current_row = []

    if current_row:
        keyboard.append(current_row)

    # Bottom navigation button to go back to main menu
    keyboard.append([KeyboardButton(text=BTN_BACK_MAIN)])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Vazifani tanlang yoki asosiy menyuga qayting...",
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Returns a simple cancel keyboard for FSM inputs."""
    keyboard = [[KeyboardButton(text=BTN_CANCEL)]]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Vazifalarni yuboring yoki bekor qiling...",
    )
