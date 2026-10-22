"""Configuration module for Intizom Bot."""

import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Token provided by @BotFather
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8926148570:AAERLgNV9Fz6TElf6VqDOd-MeMsa8e-Z3IM").strip()

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! Iltimos, .env faylida BOT_TOKEN ni belgilang.")

# Neon PostgreSQL connection URL
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_vn9giXTWZcN2@ep-bitter-fire-b5136uu8-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require",
).strip()

# Default timezone (Uzbekistan / Tashkent UTC+5)
TIMEZONE_STR: str = os.getenv("TIMEZONE", "Asia/Tashkent").strip()

try:
    BOT_TZ = ZoneInfo(TIMEZONE_STR)
except Exception:
    BOT_TZ = ZoneInfo("UTC")

# Constraints and UI settings
MAX_TASKS_LIMIT: int = 50
PAGE_SIZE: int = 6


def get_today_str() -> str:
    """Returns today's date formatted as YYYY-MM-DD in the bot's timezone."""
    return datetime.now(BOT_TZ).strftime("%Y-%m-%d")


def get_current_timestamp() -> datetime:
    """Returns current localized datetime."""
    return datetime.now(BOT_TZ).replace(tzinfo=None)
