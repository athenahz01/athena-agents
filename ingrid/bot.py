"""
Ingrid's Telegram bot — content strategy commands for @athena_hz.
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

from core.claude_client import chat as claude_chat
from core.telegram_utils import send_message
from ingrid import config

log = logging.getLogger(__name__)

_chat_history: deque = deque(maxlen=20)


# ─── Commands ────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Hey Athena! Ingrid here — your content strategist for @athena_hz.\n\n"
        "I'll send you a daily check-in at 9am ET. In between:\n\n"
        "🎨 CREATE\n"
        "/idea [topic] — Content idea with hook + strategy\n"
        "/caption <topic> — Draft a caption\n"
        "/caption_cn <topic> — Bilingual caption\n"
        "/hooks <topic> — 5 hook variations\n\n"
        "🔥 STRATEGY\n"
        "/viral [reference] — Viral scan for your niche\n"
        "/trending — What's hot on IG\n"
        "/repurpose <content> — Multiply a post\n"
        "/calendar — Weekly content calendar\n"
        "/review <how it did> — Post performance analysis\n\n"
        "💾 LIBRARY\n"
        "/save <note or link> — Save to Inspo Lab\n"
        "/inspo — Browse Inspo Lab\n"
        "/inspo search <query> — Search inspo\n"
        "/logpost <description> — Log a post\n\n"
        "/checkin — Get today's check-in now\n"
        "/help — All commands\n\n"
        "Or text me anything content-related 💬\n\n"
        "Schedule/weather → Moana 🌊 · Finance → Stella 💰"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 <b>Ingrid — Command Menu</b>\n\n"
        "🌅 <b>Daily</b>\n"
        "/checkin — Today's strategic check-in (auto-sends 9am ET)\n\n"
        "🎨 <b>Create</b>\n"
        "/idea [topic] — Strategic content idea\n"
        "/caption &lt;topic&gt; — Draft caption\n"
        "/caption_cn &lt;topic&gt; — Bilingual caption\n"
        "/hooks &lt;topic&gt; — A/B hook variations\n\n"
        "🔥 <b>Strategy</b>\n"
        "/viral [ref] — Viral scan (or analyze a reference)\n"
        "/trending — Trending formats + audios\n"
        "/repurpose &lt;content&gt; — Repurpose suggestions\n"
        "/calendar — Weekly content calendar\n"
        "/review &lt;description&gt; — Post performance analysis\n\n"
        "💾 <b>Inspo Lab</b>\n"
        "/save &lt;note or link&gt; — Save inspiration\n"
        "/inspo — Browse recent saves\n"
        "/inspo search &lt;word&gt; — Filter by keyword\n"
        "/inspo &lt;id&gt; — Full breakdown of saved item\n"
        "/inspo_delete &lt;id&gt; — Remove a saved item\n\n"
        "📝 <b>Track</b>\n"
        "/logpost &lt;description&gt; — Log what you posted\n\n"
        "💬 Or text me anything about content!\n\n"
        "<i>Schedule → Moana 🌊 | Finance → Stella 💰</i>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else None
    await update.message.reply_text("📸 Cooking up an idea...")

    from ingrid.services.content_ideas import generate_idea

    try:
        result = generate_idea(topic)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Idea failed: {e}")
        await update.message.reply_text("😅 Idea engine stalled. Try again?")


async def cmd_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else ""
    if not topic:
        await update.message.reply_text("Usage: /caption <what the post is about>")
        return

    from ingrid.services.captions import draft_caption

    try:
        result = draft_caption(topic, bilingual=False)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Caption failed: {e}")
        await update.message.reply_text("😅 Caption drafting failed. Try again?")


async def cmd_caption_cn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else ""
    if not topic:
        await update.message.reply_text("Usage: /caption_cn <what the post is about>")
        return

    from ingrid.services.captions import draft_caption

    try:
        result = draft_caption(topic, bilingual=True)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Bilingual caption failed: {e}")
        await update.message.reply_text("😅 Caption drafting failed. Try again?")


async def cmd_hooks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else ""
    if not topic:
        await update.message.reply_text("Usage: /hooks <reel topic>")
        return

    await update.message.reply_text("📸 Generating hook variations...")

    from ingrid.services.hooks import generate_hooks

    try:
        result = generate_hooks(topic)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Hooks failed: {e}")
        await update.message.reply_text("😅 Hook generation failed. Try again?")


async def cmd_trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    niche = " ".join(context.args) if context.args else None
    await update.message.reply_text("📸 Scanning what's trending...")

    from ingrid.services.trending import get_trending

    try:
        result = get_trending(niche)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Trending failed: {e}")
        await update.message.reply_text("😅 Trend scan failed. Try again?")


async def cmd_repurpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = " ".join(context.args) if context.args else ""
    if not content:
        await update.message.reply_text(
            "Usage: /repurpose <describe the content>\n"
            "Example: /repurpose OOTD reel that got 5k views showing spring outfits"
        )
        return

    from ingrid.services.repurpose import suggest_repurpose

    try:
        result = suggest_repurpose(content)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Repurpose failed: {e}")
        await update.message.reply_text("😅 Repurpose analysis failed. Try again?")


async def cmd_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Building your content calendar...")

    from ingrid.services.calendar import generate_calendar

    try:
        result = generate_calendar(days=7)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Calendar failed: {e}")
        await update.message.reply_text("😅 Calendar generation failed. Try again?")


async def cmd_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = " ".join(context.args) if context.args else ""
    if not description:
        await update.message.reply_text(
            "Usage: /review <describe how the post did>\n"
            "Example: /review my OOTD reel got 3k views 150 likes 20 saves but only 5 comments"
        )
        return

    from ingrid.services.review import review_post

    try:
        result = review_post(description)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Review failed: {e}")
        await update.message.reply_text("😅 Review analysis failed. Try again?")


async def cmd_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """On-demand version of the daily 9am check-in."""
    await update.message.reply_text("📸 Reviewing your activity...")

    from ingrid.services.proactive import build_checkin

    try:
        message = build_checkin()
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
    except Exception as e:
        log.error(f"Checkin failed: {e}")
        await update.message.reply_text("😅 Check-in stalled. Try again?")


async def cmd_viral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Viral scan — general niche or deep-dive on a reference."""
    reference = " ".join(context.args) if context.args else ""
    await update.message.reply_text("📸 Running viral scan...")

    from ingrid.services.viral_scan import scan_niche, analyze_reference

    try:
        if reference:
            result = analyze_reference(reference)
        else:
            result = scan_niche()
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Viral scan failed: {e}")
        await update.message.reply_text("😅 Viral scan failed. Try again?")


async def cmd_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save to Inspo Lab."""
    note = " ".join(context.args) if context.args else ""
    if not note:
        await update.message.reply_text(
            "Usage: /save <note or link>\n"
            "Example: /save https://instagram.com/reel/xyz — love the transition timing"
        )
        return

    await update.message.reply_text("💾 Saving to Inspo Lab...")

    from ingrid.services.inspo_lab import save_item

    try:
        result = save_item(note)
        await update.message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        log.error(f"Save failed: {e}")
        await update.message.reply_text("😅 Save failed. Try again?")


async def cmd_inspo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Browse / search / view Inspo Lab."""
    from ingrid.services.inspo_lab import list_recent, search, get_by_id

    args = context.args or []

    try:
        # /inspo → list recent
        if not args:
            result = list_recent(n=10)
        # /inspo search <query>
        elif args[0].lower() == "search" and len(args) > 1:
            result = search(" ".join(args[1:]))
        # /inspo <id>
        elif args[0].isdigit():
            result = get_by_id(int(args[0]))
        else:
            # treat as search query
            result = search(" ".join(args))

        await _send_long_html(update, result)
    except Exception as e:
        log.error(f"Inspo browse failed: {e}")
        await update.message.reply_text("😅 Inspo lookup failed. Try again?")


async def cmd_inspo_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove an inspo item by id."""
    args = context.args or []
    if not args or not args[0].isdigit():
        await update.message.reply_text("Usage: /inspo_delete <id>")
        return

    from ingrid.services.inspo_lab import delete

    result = delete(int(args[0]))
    await update.message.reply_text(result)


async def cmd_logpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = " ".join(context.args) if context.args else ""
    if not description:
        await update.message.reply_text(
            "Usage: /logpost <what you posted>\n"
            "Example: /logpost reel - spring outfit transition with trending audio"
        )
        return

    from ingrid.services.calendar import log_post

    # Try to detect format from description
    desc_lower = description.lower()
    if "reel" in desc_lower:
        fmt = "Reel"
    elif "carousel" in desc_lower:
        fmt = "Carousel"
    elif "story" in desc_lower:
        fmt = "Story"
    else:
        fmt = "Post"

    log_post(description, fmt)
    await update.message.reply_text(f"📝 Logged: {description}\nFormat: {fmt}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free-text → Claude with Ingrid's personality."""
    user_text = update.message.text
    if not user_text:
        return

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
        await _send_long(update, response)
    except Exception as e:
        log.error(f"Chat failed: {e}")
        await update.message.reply_text("😅 My brain glitched. Try again?")


# ─── Helpers ─────────────────────────────────────────────────

async def _send_long(update: Update, text: str):
    """Send a long message, splitting if needed."""
    MAX = 4000
    while len(text) > MAX:
        split = text.rfind("\n", 0, MAX)
        if split == -1:
            split = MAX
        await update.message.reply_text(text[:split])
        text = text[split:].lstrip("\n")
    if text.strip():
        await update.message.reply_text(text)


async def _send_long_html(update: Update, text: str):
    """Same as _send_long but parses HTML, with plain-text fallback per chunk."""
    MAX = 4000
    chunks = []
    while len(text) > MAX:
        split = text.rfind("\n", 0, MAX)
        if split == -1:
            split = MAX
        chunks.append(text[:split])
        text = text[split:].lstrip("\n")
    if text.strip():
        chunks.append(text)

    for chunk in chunks:
        try:
            await update.message.reply_text(chunk, parse_mode=ParseMode.HTML)
        except Exception as e:
            log.warning(f"HTML send failed, falling back to plain: {e}")
            await update.message.reply_text(chunk)


# ─── Registration ────────────────────────────────────────────

async def set_commands(app: Application):
    await app.bot.set_my_commands([
        BotCommand("checkin", "Today's strategic check-in"),
        BotCommand("idea", "Content idea + strategy"),
        BotCommand("caption", "Draft a caption"),
        BotCommand("caption_cn", "Bilingual caption"),
        BotCommand("hooks", "A/B hook variations"),
        BotCommand("viral", "Viral scan for your niche"),
        BotCommand("trending", "What's trending on IG"),
        BotCommand("repurpose", "Repurpose content"),
        BotCommand("calendar", "Weekly content calendar"),
        BotCommand("review", "Analyze post performance"),
        BotCommand("save", "Save to Inspo Lab"),
        BotCommand("inspo", "Browse Inspo Lab"),
        BotCommand("inspo_delete", "Delete an inspo item"),
        BotCommand("logpost", "Log what you posted"),
        BotCommand("help", "All commands"),
    ])


def register_handlers(app: Application):
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("checkin", cmd_checkin))
    app.add_handler(CommandHandler("idea", cmd_idea))
    app.add_handler(CommandHandler("caption", cmd_caption))
    app.add_handler(CommandHandler("caption_cn", cmd_caption_cn))
    app.add_handler(CommandHandler("hooks", cmd_hooks))
    app.add_handler(CommandHandler("viral", cmd_viral))
    app.add_handler(CommandHandler("trending", cmd_trending))
    app.add_handler(CommandHandler("repurpose", cmd_repurpose))
    app.add_handler(CommandHandler("calendar", cmd_calendar))
    app.add_handler(CommandHandler("review", cmd_review))
    app.add_handler(CommandHandler("save", cmd_save))
    app.add_handler(CommandHandler("inspo", cmd_inspo))
    app.add_handler(CommandHandler("inspo_delete", cmd_inspo_delete))
    app.add_handler(CommandHandler("logpost", cmd_logpost))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
