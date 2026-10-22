"""Statistics handler for tracking user discipline and streaks."""

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import get_today_str
from database import db
from keyboards.inline import build_stats_keyboard
from keyboards.reply import (
    BTN_STATS,
    get_checklist_reply_keyboard,
    get_main_menu_keyboard,
)
from utils.helpers import build_progress_bar, get_random_quote

router = Router(name="stats_router")


async def render_stats_text(user_id: int) -> str:
    """Builds formatted HTML string for the user's statistics."""
    today_str = get_today_str()
    stats = await db.get_user_stats(user_id, today_str)

    if stats["total_active"] == 0:
        return (
            "📊 <b>Statistika:</b>\n\n"
            "⚠️ Sizda hali birorta ham intizomiy vazifa yo‘q.\n"
            "Avval <b>«📝 Topshiriqlarni kiritish»</b> bo‘limida vazifalarni belgilang!"
        )

    progress_bar = build_progress_bar(stats["today_percentage"])
    quote = get_random_quote()

    text = (
        f"📊 <b>Sizning intizom statistikangiz</b>\n\n"
        f"📅 Sana: <code>{today_str}</code>\n"
        f"📈 Bugungi intizom: {progress_bar}\n\n"
        f"<b>Bugungi hisobot:</b>\n"
        f"• ✅ Bajarilgan: <b>{stats['today_done']}</b> ta\n"
        f"• ❌ Bajarilmagan: <b>{stats['today_missed']}</b> ta\n"
        f"• ⬜ Kutilmoqda: <b>{stats['today_unmarked']}</b> ta\n"
        f"• 📋 Jami faol vazifalar: <b>{stats['total_active']}</b> ta\n\n"
        f"<b>Umumiy ko‘rsatkichlar:</b>\n"
        f"• 🔥 Ketma-ketlik (Streak): <b>{stats['streak']} kun</b>\n"
        f"• 🏆 Barcha vaqtlar bo‘yicha bajarilgan: <b>{stats['all_time_done']}</b> marta\n"
        f"• 📉 O‘tkazib yuborilgan: <b>{stats['all_time_missed']}</b> marta\n\n"
        f"💡 <i>{quote}</i>"
    )
    return text


@router.message(F.text == BTN_STATS)
@router.message(Command("stats"))
async def open_stats(message: Message) -> None:
    """Entry point for viewing statistics."""
    user = message.from_user
    if not user:
        return

    text = await render_stats_text(user.id)
    await message.answer(
        text=text,
        reply_markup=build_stats_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "stats:refresh")
async def handle_stats_refresh(callback: CallbackQuery) -> None:
    """Refreshes statistics message."""
    user_id = callback.from_user.id
    text = await render_stats_text(user_id)

    try:
        if callback.message:
            await callback.message.edit_text(
                text=text,
                reply_markup=build_stats_keyboard(),
                parse_mode="HTML",
            )
    except TelegramBadRequest:
        pass
    await callback.answer("Statistika yangilandi! 🔄")


@router.callback_query(F.data == "stats:to_checklist")
async def handle_switch_from_stats_to_checklist(callback: CallbackQuery) -> None:
    """Switches directly from statistics to the bottom checklist keyboard view."""
    user_id = callback.from_user.id
    today_str = get_today_str()
    tasks = await db.get_user_tasks(user_id)

    if not tasks:
        await callback.answer("Hali vazifalar kiritilmagan!", show_alert=True)
        return

    logs = await db.get_daily_logs_map(user_id, today_str)
    done_count = sum(1 for t in tasks if logs.get(t["id"]) == "done")
    total_count = len(tasks)

    if callback.message:
        await callback.message.answer(
            text=(
                f"📅 <b>Bugungi intizom chek-listi</b> — <code>{today_str}</code>\n"
                f"📊 Holat: <b>{done_count}/{total_count}</b> bajarildi.\n\n"
                "Quyidagi klaviaturadan belgilamoqchi bo‘lgan vazifangizni tanlang 👇"
            ),
            reply_markup=get_checklist_reply_keyboard(tasks, logs),
            parse_mode="HTML",
        )
    await callback.answer()
