"""
📸 Ingrid — Athena's Content & Social Media Strategist
Entry point: python -m ingrid
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

from telegram.ext import Application

from core.telegram_utils import send_message
from ingrid import config
from ingrid.bot import register_handlers, set_commands

# ─── Logging ─────────────────────────────────────────────────

log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "ingrid.log", encoding="utf-8"),
        logging.StreamHandler(
            open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
        ),
    ],
)
log = logging.getLogger("ingrid")

ET = timezone(timedelta(hours=-4))


def _now_et() -> datetime:
    return datetime.now(ET)


# ─── Weekly content recap (Sunday 7 PM) ─────────────────────

async def send_weekly_content_recap(app: Application):
    """Send a weekly content strategy nudge on Sunday evening."""
    from core.claude_client import oneshot

    try:
        # Load post history for context
        from ingrid.services.calendar import _load_history
        history = _load_history()
        recent = history[-10:] if history else []

        history_str = ""
        if recent:
            history_str = "Recent posts logged:\n"
            for h in recent:
                history_str += f"- {h['date'][:10]}: {h['description']} ({h['format']})\n"
        else:
            history_str = "No posts logged this week."

        prompt = f"""It's Sunday evening. Give Athena a quick weekly content recap and plan for @athena_hz.

{history_str}

Include:
1. Quick assessment of this week's posting (consistent? gaps? variety?)
2. One key insight or pattern you noticed
3. Top priority content idea for Monday
4. One thing to try differently next week

Keep it under 200 words. Be direct, strategic, no fluff.
"""

        recap = oneshot(
            api_key=config.ANTHROPIC_API_KEY,
            model=config.CLAUDE_MODEL,
            prompt=prompt,
            system_prompt=config.SYSTEM_PROMPT,
            max_tokens=500,
        )

        msg = f"📸 <b>Ingrid — Weekly Content Recap</b>\n\n{recap}"
        await send_message(app, config.TELEGRAM_CHAT_ID, msg)
        log.info("✅ Weekly content recap sent!")

    except Exception as e:
        log.error(f"❌ Weekly content recap failed: {e}", exc_info=True)


# ─── Scheduler ───────────────────────────────────────────────

async def scheduler_loop(app: Application):
    """Simple scheduler — Sunday 7 PM content recap."""
    recap_sent_this_week = False
    last_date = None

    while True:
        now = _now_et()
        today = now.strftime("%Y-%m-%d")

        if today != last_date:
            if now.weekday() == 0:  # Monday reset
                recap_sent_this_week = False
            last_date = today

        # Sunday 7 PM content recap
        if (
            not recap_sent_this_week
            and now.weekday() == 6
            and now.hour == 19
            and now.minute >= 0
        ):
            await send_weekly_content_recap(app)
            recap_sent_this_week = True

        await asyncio.sleep(30)


# ─── Main ────────────────────────────────────────────────────

async def main():
    log.info("📸 Starting Ingrid...")

    if not config.TELEGRAM_BOT_TOKEN:
        log.error("INGRID_TELEGRAM_BOT_TOKEN not set!")
        sys.exit(1)
    if not config.TELEGRAM_CHAT_ID:
        log.error("INGRID_TELEGRAM_CHAT_ID not set!")
        sys.exit(1)

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    register_handlers(app)

    await app.initialize()
    await app.start()

    try:
        await set_commands(app)
        log.info("✅ Bot commands registered")
    except Exception as e:
        log.warning(f"Could not set bot commands: {e}")

    await app.updater.start_polling(drop_pending_updates=True)
    log.info("🤖 Polling for messages...")

    now = _now_et()
    log.info(f"🕐 Current ET: {now.strftime('%I:%M %p')}")

    # Startup message — after everything works
    try:
        await send_message(
            app,
            config.TELEGRAM_CHAT_ID,
            "📸 Ingrid is online! Your content strategist for @athena_hz.\nType /help for commands.",
        )
    except Exception as e:
        log.warning(f"Startup message failed: {e}")

    try:
        await scheduler_loop(app)
    except (KeyboardInterrupt, SystemExit):
        log.info("📸 Ingrid shutting down...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
