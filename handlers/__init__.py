"""Handlers package."""

from aiogram import Dispatcher
from .start import router as start_router
from .setup_tasks import router as setup_tasks_router
from .checklist import router as checklist_router
from .stats import router as stats_router


def register_all_handlers(dp: Dispatcher) -> None:
    """Includes all handler routers into the main dispatcher."""
    # Register setup_tasks first so FSM states take precedence over generic text commands
    dp.include_router(setup_tasks_router)
    dp.include_router(checklist_router)
    dp.include_router(stats_router)
    dp.include_router(start_router)


__all__ = [
    "register_all_handlers",
    "start_router",
    "setup_tasks_router",
    "checklist_router",
    "stats_router",
]
