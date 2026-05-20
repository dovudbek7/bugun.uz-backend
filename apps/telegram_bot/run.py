"""
Telegram bot entry point.
Run with: python -m apps.telegram_bot.run
"""
import asyncio
import logging
import os
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def _wait_for_db(max_attempts=30):
    """Wait until PostgreSQL is ready. Skipped when SQLite is configured."""
    host = os.environ.get("POSTGRES_HOST")
    if not host:
        logging.info("SQLite mode — skipping DB wait.")
        return

    import psycopg2

    params = {
        "dbname": os.environ.get("POSTGRES_DB", "bugun"),
        "user": os.environ.get("POSTGRES_USER", "bugun"),
        "password": os.environ.get("POSTGRES_PASSWORD", "bugun"),
        "host": host,
        "port": os.environ.get("POSTGRES_PORT", "5432"),
    }
    for attempt in range(1, max_attempts + 1):
        try:
            conn = psycopg2.connect(**params)
            conn.close()
            logging.info("Database ready.")
            return
        except psycopg2.OperationalError:
            logging.info("Waiting for database... (%d/%d)", attempt, max_attempts)
            time.sleep(2)
    logging.error("Database not available after %d attempts. Exiting.", max_attempts)
    sys.exit(1)


_wait_for_db()

import django  # noqa: E402

django.setup()

from aiogram import Bot, Dispatcher  # noqa: E402
from aiogram.client.default import DefaultBotProperties  # noqa: E402
from aiogram.enums import ParseMode  # noqa: E402
from aiogram.fsm.storage.memory import MemoryStorage  # noqa: E402
from django.conf import settings  # noqa: E402

from apps.telegram_bot.handlers import games, help, location, profile, start  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)


async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(games.router)
    dp.include_router(location.router)
    dp.include_router(help.router)

    logging.info("Bot starting polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
