"""Start and general handlers for Intizom Bot."""

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from database import db
from keyboards.reply import get_main_menu_keyboard
from utils.helpers import get_random_quote

router = Router(name="start_router")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Handles the /start command, registers user, and sends welcome message."""
    user = message.from_user
    if not user:
        return

    user_id = user.id
    full_name = user.full_name or "Foydalanuvchi"

    # Save or update user in database
    await db.upsert_user(user_id=user_id, full_name=full_name)

    quote = get_random_quote()

    welcome_text = (
        f"Assalomu alaykum, <b>{full_name}</b>! 🌟\n\n"
        "«<b>Intizom Bot</b>»ga xush kelibsiz! Ushbu bot sizga kunlik intizom, "
        "foydali odatlar va vazifalaringizni muntazam nazorat qilib borishga yordam beradi.\n\n"
        f"💡 <i>{quote}</i>\n\n"
        "<b>Boshlash uchun:</b>\n"
        "1. <b>📝 Topshiriqlarni kiritish</b> tugmasi orqali har kungi odatlaringizni kiriting.\n"
        "2. <b>✅ Kunlik Intizom Chek-list</b> orqali har kuni ularning bajarilishini belgilab boring.\n"
        "3. <b>📊 Statistikam</b> orqali o‘z natijalaringiz va intizom ko‘rsatkichingizni kuzating!\n\n"
        "Kerakli bo‘limni tanlang 👇"
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Provides instructions on how to use the bot."""
    help_text = (
        "📖 <b>«Intizom Bot» qo‘llanmasi:</b>\n\n"
        "• <b>📝 Topshiriqlarni kiritish</b> — Kunlik intizomiy rejangizni kiritasiz (masalan: <i>Namoz, Kitob o‘qish, Sport</i>). Har bir vazifani alohida yangi qatordan yozing (50 tagacha).\n\n"
        "• <b>✅ Kunlik Intizom Chek-list</b> — Bugungi vazifalar ro‘yxati. Har bir vazifani ✅ (bajarildi) yoki ❌ (o‘tkazib yuborildi) qilib belgilashingiz mumkin. Tugmani to‘g‘ridan-to‘g‘ri bosish orqali ham holatni tezkor almashtirish mumkin.\n\n"
        "• <b>📊 Statistikam</b> — Bugungi va umumiy intizom natijalaringiz, bajarilgan foiz va ketma-ketlik (streak) ko‘rsatkichi.\n\n"
        "Har qanday vaqtda /start orqali asosiy menyuga qaytishingiz mumkin."
    )
    await message.answer(
        text=help_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )
