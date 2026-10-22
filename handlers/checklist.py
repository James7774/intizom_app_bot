"""Checklist handlers for interactive daily habit tracking using Reply Keyboard."""

import re
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import get_today_str
from database import db
from keyboards.inline import build_task_confirmation_keyboard
from keyboards.reply import (
    BTN_CHECKLIST,
    BTN_BACK_MAIN,
    BTN_SETUP_TASKS,
    BTN_STATS,
    BTN_CANCEL,
    get_checklist_reply_keyboard,
    get_main_menu_keyboard,
)

router = Router(name="checklist_router")


@router.message(F.text == BTN_CHECKLIST)
@router.message(Command("checklist"))
async def open_checklist(message: Message) -> None:
    """
    Replaces bottom keyboard with user's daily tasks.
    Each task is shown as a button with its status emoji (✅, ❌, or ⬜).
    """
    user = message.from_user
    if not user:
        return

    user_id = user.id
    today_str = get_today_str()
    tasks = await db.get_user_tasks(user_id)

    if not tasks:
        await message.answer(
            text=(
                "⚠️ <b>Sizda hali birorta ham intizomiy vazifa yo‘q.</b>\n\n"
                "Iltimos, avval <b>«📝 Topshiriqlarni kiritish»</b> tugmasi orqali "
                "kunlik vazifalaringizni kiriting."
            ),
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    logs = await db.get_daily_logs_map(user_id, today_str)
    done_count = sum(1 for t in tasks if logs.get(t["id"]) == "done")
    total_count = len(tasks)

    msg_text = (
        f"📅 <b>Bugungi intizom chek-listi</b> — <code>{today_str}</code>\n"
        f"📊 Holat: <b>{done_count}/{total_count}</b> bajarildi.\n\n"
        "Quyidagi klaviaturadan belgilamoqchi bo‘lgan vazifangizni tanlang 👇"
    )

    await message.answer(
        text=msg_text,
        reply_markup=get_checklist_reply_keyboard(tasks, logs),
        parse_mode="HTML",
    )


@router.message(F.text == BTN_BACK_MAIN)
async def back_to_main_menu(message: Message) -> None:
    """Switches bottom keyboard back to the main menu."""
    await message.answer(
        text="Asosiy menyudasiz 👇",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(
    F.text
    & ~F.text.startswith("/")
    & (F.text != BTN_SETUP_TASKS)
    & (F.text != BTN_CHECKLIST)
    & (F.text != BTN_STATS)
    & (F.text != BTN_CANCEL)
    & (F.text != BTN_BACK_MAIN)
)
async def handle_task_button_click(message: Message) -> None:
    """
    Handles when user clicks on a task button from the bottom reply keyboard.
    Sends a simple chat question: '[Vazifa nomi]ni bajardingizmi?' with [ ✅ ] and [ ❌ ].
    """
    user = message.from_user
    if not user or not message.text:
        return

    user_id = user.id
    today_str = get_today_str()
    tasks = await db.get_user_tasks(user_id)

    if not tasks:
        return

    # Strip leading status icons (✅, ❌, ⬜) and whitespace
    cleaned_input = re.sub(r"^[✅❌⬜▫️\s]+", "", message.text).strip().lower()

    # Find the corresponding task
    matched_task = None
    for t in tasks:
        t_name = t["task_name"].strip().lower()
        if t_name == cleaned_input or t_name == message.text.strip().lower():
            matched_task = t
            break

    if not matched_task:
        # If user typed something unrelated, let other handlers or ignore
        return

    task_id = matched_task["id"]
    task_name = matched_task["task_name"]

    logs = await db.get_daily_logs_map(user_id, today_str)
    current_status = logs.get(task_id)

    status_note = ""
    if current_status == "done":
        status_note = "\n<i>(Hozirgi holat: ✅ Bajargansiz)</i>"
    elif current_status == "missed":
        status_note = "\n<i>(Hozirgi holat: ❌ Bajarilmagan deb belgilangan)</i>"

    prompt_text = (
        f"📖 <b>{task_name}</b>{status_note}\n\n"
        f"Bugun ushbu vazifani bajardingizmi?"
    )

    await message.answer(
        text=prompt_text,
        reply_markup=build_task_confirmation_keyboard(task_id),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("ans:"))
async def handle_task_answer(callback: CallbackQuery) -> None:
    """
    Handles user tapping [ ✅ Bajardim ] or [ ❌ Bajarmadim ].
    Updates the database and updates the user's bottom reply keyboard.
    """
    user_id = callback.from_user.id
    today_str = get_today_str()
    parts = callback.data.split(":")
    task_id = int(parts[1])
    action = parts[2]  # 'done' or 'missed'

    task = await db.get_task_by_id(task_id)
    task_name = task["task_name"] if task else "Vazifa"

    if action == "done":
        await db.set_task_status(user_id, task_id, today_str, "done")
        toast = "Barakalla! ✅"
        result_text = f"✅ <b>{task_name}</b> — <b>Bajarildi</b> deb saqlandi! Barakalla! 🎯"
    else:
        await db.set_task_status(user_id, task_id, today_str, "missed")
        toast = "Bajarilmadi deb belgilandi! ❌"
        result_text = f"❌ <b>{task_name}</b> — <b>Bajarilmadi</b> deb belgilandi."

    # Update the inline message in chat
    try:
        if callback.message:
            await callback.message.edit_text(
                text=result_text,
                parse_mode="HTML",
            )
    except TelegramBadRequest:
        pass

    await callback.answer(toast)

    # Fetch updated tasks and logs to refresh the bottom reply keyboard
    tasks = await db.get_user_tasks(user_id)
    logs = await db.get_daily_logs_map(user_id, today_str)
    done_count = sum(1 for t in tasks if logs.get(t["id"]) == "done")
    total_count = len(tasks)

    # Send a quick follow-up message with the refreshed keyboard
    if callback.message:
        await callback.message.answer(
            text=(
                f"📊 Bugungi natija: <b>{done_count}/{total_count}</b> bajarildi.\n"
                "Keyingi vazifani tanlang yoki asosiy menyuga qayting 👇"
            ),
            reply_markup=get_checklist_reply_keyboard(tasks, logs),
            parse_mode="HTML",
        )
