"""
Moana's Telegram bot — handles commands and free-text chat.
Scoped to Moana's responsibilities: weather, news, calendar, deadlines, translate, chat.
Redirects content/finance questions to Ingrid/Stella.
"""

import logging
from collections import deque

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

from core.claude_client import chat as claude_chat, oneshot as claude_oneshot
from core.telegram_utils import send_message
from moana import config

log = logging.getLogger(__name__)

# Conversation history for free-text chat (resets on restart)
_chat_history: deque = deque(maxlen=20)


# ─── Commands ────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌊 Hey Athena! Moana here — your Chief of Staff.\n\n"
        "I handle your daily rhythm:\n"
        "/brief — Full morning brief\n"
        "/weather — Ithaca weather + outfit tip\n"
        "/news — Latest headlines\n"
        "/deadlines — Upcoming deadlines\n"
        "/remind <text> — Quick reminder\n"
        "/cn <text> — EN↔CN translate\n"
        "/priorities — Today's top 3\n"
        "/help — All commands\n\n"
        "For content/IG stuff → ask Ingrid 📸\n"
        "For finance/stocks → ask Stella 💰\n\n"
        "Or just text me anything 💬"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌊 <b>Moana — Command Menu</b>\n\n"
        "📋 <b>Daily</b>\n"
        "/brief — Full morning brief\n"
        "/weather — Ithaca weather + outfit\n"
        "/news — Curated headlines\n\n"
        "📌 <b>Productivity</b>\n"
        "/deadlines — Upcoming deadlines\n"
        "/remind &lt;text&gt; — Set a reminder\n"
        "/priorities — Today's top 3\n\n"
        "🔧 <b>Utilities</b>\n"
        "/cn &lt;text&gt; — Translate EN↔CN\n\n"
        "💬 Or just text me anything!\n\n"
        "<i>Content/IG → Ingrid 📸 | Finance → Stella 💰</i>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_brief(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌊 Brewing your brief, one sec...")
    from moana.services.brief_builder import build_morning_brief
    from moana.formatters.telegram_formatter import format_full_brief

    try:
        data = build_morning_brief()
        for msg in format_full_brief(data):
            await update.message.reply_text(
                msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True
            )
    except Exception as e:
        log.error(f"Brief failed: {e}")
        await update.message.reply_text("😅 Brief ran into an issue. Check logs!")


async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from moana.services.weather import get_weather
    from moana.formatters.telegram_formatter import format_weather_quick

    try:
        text = format_weather_quick(get_weather())
    except Exception as e:
        log.error(f"Weather failed: {e}")
        text = "😅 Couldn't fetch weather right now."
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from moana.services.news import get_all_news
    from moana.formatters.telegram_formatter import format_news_section

    try:
        text = format_news_section(get_all_news())
    except Exception as e:
        log.error(f"News failed: {e}")
        text = "😅 News fetch hiccuped, try again."
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_deadlines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from moana.services.deadlines import get_upcoming_deadlines
    from moana.formatters.telegram_formatter import format_deadlines

    text = format_deadlines(get_upcoming_deadlines())
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from moana.services.deadlines import add_reminder

    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Usage: /remind <what to remember>")
        return
    add_reminder(text)
    await update.message.reply_text(f"✅ Got it! I'll remember:\n{text}")


async def cmd_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from moana.services.translator import translate

    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Usage: /cn <text to translate>")
        return
    try:
        await update.message.reply_text(translate(text))
    except Exception as e:
        log.error(f"Translation failed: {e}")
        await update.message.reply_text("😅 Translation failed, try again.")


async def cmd_priorities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = claude_oneshot(
            api_key=config.ANTHROPIC_API_KEY,
            model=config.CLAUDE_MODEL,
            prompt=(
                "What should Athena's top 3 priorities be today? Consider her "
                "current projects: Whetstone Portal, Political Network Explorer, "
                "Cornell M.Eng coursework, and her personal website athenahuo.com. "
                "Give a focused, actionable list — no fluff."
            ),
            system_prompt=config.SYSTEM_PROMPT,
        )
        await update.message.reply_text(response)
    except Exception as e:
        log.error(f"Priorities failed: {e}")
        await update.message.reply_text("😅 Couldn't generate priorities right now.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free-text → Claude with Moana's personality."""
    user_text = update.message.text
    if not user_text:
        return

    # Only respond to Athena
    if str(update.effective_chat.id) != str(config.TELEGRAM_CHAT_ID):
        return

    try:
        response = claude_chat(
            api_key=config.ANTHROPIC_API_KEY,
            model=config.CLAUDE_MODEL,
            system_prompt=config.SYSTEM_PROMPT,
            user_message=user_text,
            history=_chat_history,
        )
        await update.message.reply_text(response)
    except Exception as e:
        log.error(f"Chat failed: {e}")
        await update.message.reply_text("😅 My brain glitched for a sec. Try again?")


# ─── Registration ────────────────────────────────────────────

async def set_commands(app: Application):
    await app.bot.set_my_commands([
        BotCommand("brief", "Full morning brief"),
        BotCommand("weather", "Ithaca weather"),
        BotCommand("news", "Curated headlines"),
        BotCommand("deadlines", "Upcoming deadlines"),
        BotCommand("remind", "Set a reminder"),
        BotCommand("cn", "Translate EN↔CN"),
        BotCommand("priorities", "Today's top 3"),
        BotCommand("help", "All commands"),
    ])


def register_handlers(app: Application):
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("brief", cmd_brief))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("news", cmd_news))
    app.add_handler(CommandHandler("deadlines", cmd_deadlines))
    app.add_handler(CommandHandler("remind", cmd_remind))
    app.add_handler(CommandHandler("cn", cmd_translate))
    app.add_handler(CommandHandler("priorities", cmd_priorities))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
