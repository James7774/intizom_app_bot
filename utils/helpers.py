"""Helper utilities for Intizom Bot."""

import re
import random
from typing import List

# Inspiring discipline quotes in Uzbek
DISCIPLINE_QUOTES: List[str] = [
    "«Intizom — bu orzular va muvaffaqiyatlar orasidagi mustahkam ko‘prikdir.»",
    "«Har kuni kichik odatlarni bajarish — buyuk natijalarning yashirin siri.»",
    "«Bugungi dangasalik — ertangi pushaymonlikdir. Intizomingizni yo‘qotmang!»",
    "«G‘oliblar doimo kayfiyatiga emas, intizomiga tayanadi.»",
    "«Kichik, lekin uzluksiz qadamlar ulkan cho‘qqilarga olib boradi.»",
    "«O‘zingiz ustidan nazorat o‘rnatgan kuningiz — hayotingizdagi eng buyuk g‘alabadir.»",
]


def get_random_quote() -> str:
    """Returns a random motivational quote about discipline."""
    return random.choice(DISCIPLINE_QUOTES)


def build_progress_bar(percentage: float, length: int = 10) -> str:
    """
    Renders an emoji progress bar, e.g. 🟩🟩🟩🟩⬜⬜⬜⬜⬜⬜ 40%
    """
    clamped = max(0.0, min(100.0, percentage))
    filled_count = int(round((clamped / 100.0) * length))
    empty_count = length - filled_count

    bar = ("🟩" * filled_count) + ("⬜" * empty_count)
    return f"{bar} {clamped:.0f}%"


def clean_task_line(line: str) -> str:
    """
    Cleans task line by stripping whitespace, removing leading bullets or numbers (e.g., '1.', '1)', '-', '*').
    """
    trimmed = line.strip()
    # Strip leading bullet points or numbers like "1. ", "1) ", "- ", "• ", "* "
    cleaned = re.sub(r"^(?:\d+[\.\)\-:]|\*|\-|•|\+)\s*", "", trimmed)
    return cleaned.strip()


def truncate_text(text: str, max_chars: int = 22) -> str:
    """Truncate text to fit neatly on mobile inline keyboard buttons."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].strip() + "…"
