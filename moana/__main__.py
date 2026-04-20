"""
🌊 Moana — Athena's Chief of Staff
Entry point: python -m moana

Uses a simple asyncio timer instead of APScheduler to avoid
timezone/tzdata issues on Docker slim images.
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

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

# Eastern Time as fixed UTC offset (EDT = UTC-4, EST = UTC-5)
# Using EDT; off by 1 hour in winter — close enough for a morning brief
ET = timezone(timedelta(hours=-4))


def _now_et() -> datetime:
    return datetime.now(ET)


# ─── Scheduled tasks ────────────────────────────────────────

async def send_morning_brief(app: Application):
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


async def scheduler_loop(app: Application):
    """Simple scheduler — checks every 30s if it's time to fire."""
    brief_sent_today = False
    last_date = None

    while True:
        now = _now_et()
        today = now.strftime("%Y-%m-%d")

        # Reset flag at midnight
        if today != last_date:
            brief_sent_today = False
            last_date = today

        # Morning brief
        if (
            not brief_sent_today
            and now.hour == config.BRIEF_HOUR
            and now.minute >= config.BRIEF_MINUTE
        ):
            await send_morning_brief(app)
            brief_sent_today = True

        await asyncio.sleep(30)


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

    # Start polling for messages
    await app.updater.start_polling(drop_pending_updates=True)
    log.info("🤖 Polling for messages...")

    # Scheduler info
    now = _now_et()
    log.info(f"⏰ Brief: {config.BRIEF_HOUR}:{config.BRIEF_MINUTE:02d} ET")
    log.info(f"🕐 Current ET: {now.strftime('%I:%M %p')}")

    # Startup message — ONLY after everything works
    try:
        await send_message(
            app,
            config.TELEGRAM_CHAT_ID,
            "🌊 Moana is online!\nType /help for commands.",
        )
    except Exception as e:
        log.warning(f"Startup message failed: {e}")

    # Run forever
    try:
        await scheduler_loop(app)
    except (KeyboardInterrupt, SystemExit):
        log.info("🌊 Moana shutting down...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())