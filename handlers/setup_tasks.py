"""Handlers for configuring user's daily habits and tasks using FSM."""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import MAX_TASKS_LIMIT
from database import db
from keyboards.reply import (
    BTN_SETUP_TASKS,
    BTN_CANCEL,
    get_cancel_keyboard,
    get_main_menu_keyboard,
)
from utils.helpers import clean_task_line

router = Router(name="setup_tasks_router")


class TaskSetupStates(StatesGroup):
    waiting_for_tasks = State()


@router.message(F.text == BTN_SETUP_TASKS)
@router.message(Command("set_tasks"))
async def start_task_setup(message: Message, state: FSMContext) -> None:
    """Initiates the FSM flow for setting up daily tasks."""
    user = message.from_user
    if not user:
        return

    # Check existing tasks count to give personalized context
    existing_tasks = await db.get_user_tasks(user.id)
    existing_count_text = (
        f"\n<i>(Hozirda sizda {len(existing_tasks)} ta vazifa mavjud. "
        "Yangi ro‘yxat yuborsangiz, oldingi vazifalar yangilanadi.)</i>"
        if existing_tasks
        else ""
    )

    prompt = (
        "📋 <b>Kunlik intizomiy vazifalaringizni kiriting.</b>\n\n"
        "Har bir vazifani <b>alohida yangi qatordan</b> yozing (ko‘pi bilan 50 tagacha)."
        f"{existing_count_text}\n\n"
        "<b>Misol uchun:</b>\n"
        "1. Bomdod namozi va zikr\n"
        "2. Kitob o‘qish (30 daqiqa)\n"
        "3. Jismoniy tarbiya / sport\n"
        "4. Ingliz tili / yangi so‘zlar\n"
        "5. Kod yozish amaliyoti\n\n"
        "Bekor qilish uchun quyidagi <b>«🔙 Bekor qilish»</b> tugmasini bosing yoki /cancel yozing."
    )

    await state.set_state(TaskSetupStates.waiting_for_tasks)
    await message.answer(
        text=prompt,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )


@router.message(TaskSetupStates.waiting_for_tasks, F.text == BTN_CANCEL)
@router.message(TaskSetupStates.waiting_for_tasks, Command("cancel"))
async def cancel_task_setup(message: Message, state: FSMContext) -> None:
    """Cancels the task setup flow."""
    await state.clear()
    await message.answer(
        text="❌ Vazifalarni kiritish bekor qilindi.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(TaskSetupStates.waiting_for_tasks, F.text)
async def process_task_input(message: Message, state: FSMContext) -> None:
    """Parses, validates, and saves bulk multi-line tasks to the database."""
    user = message.from_user
    if not user or not message.text:
        return

    raw_lines = message.text.split("\n")
    tasks: list[str] = []

    for line in raw_lines:
        cleaned = clean_task_line(line)
        if cleaned:
            tasks.append(cleaned)

    if not tasks:
        await message.answer(
            text="⚠️ Hech qanday to‘g‘ri vazifa topilmadi. Iltimos, kamida 1 ta vazifani yangi qatordan yozib yuboring:",
            reply_markup=get_cancel_keyboard(),
        )
        return

    # Enforce limit of 50 tasks
    was_sliced = False
    if len(tasks) > MAX_TASKS_LIMIT:
        tasks = tasks[:MAX_TASKS_LIMIT]
        was_sliced = True

    # Persist in SQLite
    saved_count = await db.set_user_tasks(user_id=user.id, task_names=tasks)
    await state.clear()

    # Build preview list
    preview_items = "\n".join(
        [f"<b>{idx}.</b> {task}" for idx, task in enumerate(tasks, 1)]
    )

    slice_notice = (
        f"\n\n<i>⚠️ Vazifalar soni maksimal chegaradan oshgani uchun birinchi {MAX_TASKS_LIMIT} tasi olindi.</i>"
        if was_sliced
        else ""
    )

    success_text = (
        f"🎯 <b>{saved_count} ta vazifa intizom rejangizga muvaffaqiyatli saqlandi!</b>{slice_notice}\n\n"
        f"<b>📋 Sizning yangi vazifalar ro‘yxatingiz:</b>\n"
        f"{preview_items}\n\n"
        "Endi har kuni <b>«✅ Kunlik Intizom Chek-list»</b> bo‘limiga kirib, bajargan ishlaringizni belgilab boring!"
    )

    await message.answer(
        text=success_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )
