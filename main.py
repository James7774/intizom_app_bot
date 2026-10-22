"""Main entry point for Intizom Bot."""

import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import db
from handlers import register_all_handlers


async def start_health_check_server() -> web.AppRunner:
    """Starts a minimal HTTP server for Koyeb/cloud health checks."""
    port = int(os.getenv("PORT", 8000))
    app = web.Application()

    async def ping_handler(request: web.Request) -> web.Response:
        return web.Response(text="OK - Intizom Bot is active!", status=200)

    app.router.add_get("/", ping_handler)
    app.router.add_get("/health", ping_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    return runner


async def set_bot_commands(bot: Bot) -> None:
    """Sets bot menu commands in Telegram UI."""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish va bosh menyu"),
        BotCommand(command="checklist", description="Bugungi intizom chek-listi"),
        BotCommand(command="set_tasks", description="Kunlik vazifalarni kiritish"),
        BotCommand(command="stats", description="Intizom statistikasi"),
        BotCommand(command="help", description="Qo‘llanma va yordam"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    """Initializes and runs the bot."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger("IntizomBot")

    # Start health check server for cloud platforms (Koyeb, Render)
    web_runner = None
    try:
        web_runner = await start_health_check_server()
        logger.info("Health-check web server started on port %s.", os.getenv("PORT", 8000))
    except Exception as e:
        logger.warning(f"Could not start health check web server: {e}")

    logger.info("Initializing database...")
    await db.init_db()
    logger.info("Database initialized successfully.")

    # Initialize Bot and Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register handlers
    register_all_handlers(dp)

    # Set bot commands in Telegram
    try:
        await set_bot_commands(bot)
        logger.info("Bot commands registered in Telegram.")
    except Exception as e:
        logger.warning(f"Could not register bot commands: {e}")

    # Drop pending updates to avoid processing stale messages
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    logger.info(
        f"Bot started successfully! Running as @{bot_info.username} (ID: {bot_info.id})"
    )

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Shutting down bot...")
        await bot.session.close()
        await db.close()
        if web_runner:
            await web_runner.cleanup()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user.")
