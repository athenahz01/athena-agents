"""
🌊 Moana — Athena's Chief of Staff
Entry point: python -m moana
"""

import asyncio
import logging
import sys
from pathlib import Path

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application

from core.telegram_utils import send_message
from moana import config
from moana.bot import register_handlers, set_commands

# ─── Logging ─────────────────────────────────────────────────

log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "moana.log", encoding="utf-8"),
        logging.StreamHandler(
            open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
        ),
    ],
)
log = logging.getLogger("moana")


# ─── Scheduled morning brief ────────────────────────────────

async def send_morning_brief(app: Application):
    """Build and send the daily morning brief."""
    log.info("🌊 Building morning brief...")

    from moana.services.brief_builder import build_morning_brief
    from moana.formatters.telegram_formatter import format_full_brief

    try:
        data = build_morning_brief()
        for msg in format_full_brief(data):
            await send_message(app, config.TELEGRAM_CHAT_ID, msg)
            await asyncio.sleep(1)
        log.info("✅ Morning brief sent!")
    except Exception as e:
        log.error(f"❌ Morning brief failed: {e}", exc_info=True)
        try:
            await send_message(
                app,
                config.TELEGRAM_CHAT_ID,
                f"😅 Morning brief hit a snag.\nError: {str(e)[:200]}",
            )
        except Exception:
            pass


async def send_weekly_recap(app: Application):
    """Build and send the Sunday weekly recap."""
    log.info("🌊 Building weekly recap...")

    from moana.services.recap_builder import build_weekly_recap
    from moana.formatters.telegram_formatter import format_weekly_recap
    from moana.services.activity import cleanup_old_data

    try:
        data = build_weekly_recap()
        await send_message(app, config.TELEGRAM_CHAT_ID, format_weekly_recap(data))
        cleanup_old_data(days_to_keep=30)
        log.info("✅ Weekly recap sent!")
    except Exception as e:
        log.error(f"❌ Weekly recap failed: {e}", exc_info=True)


# ─── Main ────────────────────────────────────────────────────

async def main():
    log.info("🌊 Starting Moana...")

    if not config.TELEGRAM_BOT_TOKEN:
        log.error("MOANA_TELEGRAM_BOT_TOKEN not set!")
        sys.exit(1)
    if not config.TELEGRAM_CHAT_ID:
        log.error("MOANA_TELEGRAM_CHAT_ID not set!")
        sys.exit(1)

    # Build Telegram app
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    register_handlers(app)

    await app.initialize()
    await app.start()

    # Set bot command menu
    try:
        await set_commands(app)
        log.info("✅ Bot commands registered")
    except Exception as e:
        log.warning(f"Could not set bot commands: {e}")

    # Startup message
    try:
        await send_message(
            app,
            config.TELEGRAM_CHAT_ID,
            "🌊 Moana is online! 早安 ☀️\nType /help for commands.",
        )
    except Exception as e:
        log.warning(f"Startup message failed: {e}")

    # Schedule daily brief
    scheduler = AsyncIOScheduler(timezone="America/New_York")
    scheduler.add_job(
        send_morning_brief,
        "cron",
        hour=config.BRIEF_HOUR,
        minute=config.BRIEF_MINUTE,
        args=[app],
        id="morning_brief",
        name="Daily Morning Brief",
        misfire_grace_time=3600,
    )

    # Schedule weekly recap — Sunday 8 PM ET
    scheduler.add_job(
        send_weekly_recap,
        "cron",
        day_of_week="sun",
        hour=20,
        minute=0,
        args=[app],
        id="weekly_recap",
        name="Weekly Recap",
        misfire_grace_time=3600,
    )

    scheduler.start()
    log.info(
        f"⏰ Brief scheduled: {config.BRIEF_HOUR}:{config.BRIEF_MINUTE:02d} {config.TIMEZONE}"
    )
    log.info("⏰ Weekly recap scheduled: Sunday 8:00 PM ET")

    # Start polling
    log.info("🤖 Polling for messages...")
    await app.updater.start_polling(drop_pending_updates=True)

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        log.info("🌊 Moana shutting down...")
    finally:
        scheduler.shutdown()
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())