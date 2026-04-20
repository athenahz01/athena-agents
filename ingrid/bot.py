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


# ─── Account-flag parser ─────────────────────────────────────

def _parse_account(args: list) -> tuple[str | None, list]:
    """Extract an account override from args.

    Flags accepted:
      --hz / --huo / @athena_hz / @athena_huo

    Returns (account, remaining_args). account is None if no flag present.
    """
    account = None
    out = []
    for a in args:
        low = a.lower()
        if low in ("--hz", "@athena_hz", "athena_hz"):
            account = "athena_hz"
        elif low in ("--huo", "@athena_huo", "athena_huo"):
            account = "athena_huo"
        else:
            out.append(a)
    return account, out


# ─── Commands ────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Hey Athena! Ingrid here — your content strategist for @athena_huo (growth) + @athena_hz (portfolio).\n\n"
        "I run the playbook: DITL format, countdown arc, playbook-compliant hooks + captions, two-account separation.\n\n"
        "Daily check-in at 9am ET. Type /help to see everything.\n\n"
        "Try:\n"
        "• /countdown — how many days to graduation\n"
        "• /idea — a content idea for today\n"
        "• /hero — plan the May 23 hero reel\n"
        "• /calendar — this week's arc-aware plan\n\n"
        "Add --hz or --huo to target the other account.\n\n"
        "Schedule/weather → Moana 🌊 · Finance → Stella 💰"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 <b>Ingrid — Command Menu</b>\n\n"
        "🌅 <b>Daily</b>\n"
        "/checkin — Today's strategic check-in (auto-sends 9am ET)\n"
        "/countdown — Arc status: days to grad, act, phase\n"
        "/hero — Plan the graduation hero reel\n\n"
        "🎨 <b>Create</b> (add --hz or --huo to target account)\n"
        "/idea [topic] — Strategic content idea\n"
        "/caption &lt;topic&gt; — DITL-compliant caption\n"
        "/caption_cn &lt;topic&gt; — Bilingual caption\n"
        "/hooks &lt;topic&gt; — Playbook hook variations\n\n"
        "🔥 <b>Strategy</b>\n"
        "/viral [ref] — Viral scan or analyze a reference\n"
        "/trending — Trending audios/formats (playbook-filtered)\n"
        "/repurpose &lt;content&gt; — Multiply one piece of content\n"
        "/calendar — Arc-aware weekly content calendar\n"
        "/review &lt;description&gt; — Post analysis via playbook KPIs\n\n"
        "💾 <b>Inspo Lab</b>\n"
        "/save &lt;note or link&gt; — Save + auto-tag + breakdown\n"
        "/inspo — Browse recent saves\n"
        "/inspo search &lt;word&gt; — Filter by keyword\n"
        "/inspo &lt;id&gt; — Full breakdown\n"
        "/inspo_delete &lt;id&gt; — Remove\n\n"
        "📝 <b>Track</b>\n"
        "/logpost &lt;description&gt; — Log a post (account auto-detected)\n\n"
        "💡 <b>Tip:</b> Add <code>--hz</code> or <code>--huo</code> to any create/review command to target the other account.\n\n"
        "💬 Or text me anything about content!\n\n"
        "<i>Schedule → Moana 🌊 | Finance → Stella 💰</i>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account, rest = _parse_account(context.args or [])
    topic = " ".join(rest) if rest else None
    await update.message.reply_text(f"📸 Cooking up an idea for @{account or 'athena_huo'}...")

    from ingrid.services.content_ideas import generate_idea

    try:
        result = generate_idea(topic, account=account)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Idea failed: {e}")
        await update.message.reply_text("😅 Idea engine stalled. Try again?")


async def cmd_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account, rest = _parse_account(context.args or [])
    topic = " ".join(rest) if rest else ""
    if not topic:
        await update.message.reply_text(
            "Usage: /caption [--hz|--huo] <what the post is about>"
        )
        return

    from ingrid.services.captions import draft_caption

    try:
        result = draft_caption(topic, bilingual=False, account=account)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Caption failed: {e}")
        await update.message.reply_text("😅 Caption drafting failed. Try again?")


async def cmd_caption_cn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account, rest = _parse_account(context.args or [])
    topic = " ".join(rest) if rest else ""
    if not topic:
        await update.message.reply_text(
            "Usage: /caption_cn [--hz|--huo] <what the post is about>"
        )
        return

    from ingrid.services.captions import draft_caption

    try:
        result = draft_caption(topic, bilingual=True, account=account)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Bilingual caption failed: {e}")
        await update.message.reply_text("😅 Caption drafting failed. Try again?")


async def cmd_hooks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account, rest = _parse_account(context.args or [])
    topic = " ".join(rest) if rest else ""
    if not topic:
        await update.message.reply_text("Usage: /hooks [--hz|--huo] <reel topic>")
        return

    await update.message.reply_text(f"📸 Generating hooks for @{account or 'athena_huo'}...")

    from ingrid.services.hooks import generate_hooks

    try:
        result = generate_hooks(topic, account=account)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Hooks failed: {e}")
        await update.message.reply_text("😅 Hook generation failed. Try again?")


async def cmd_trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account, rest = _parse_account(context.args or [])
    niche = " ".join(rest) if rest else None
    await update.message.reply_text("📸 Scanning what's trending...")

    from ingrid.services.trending import get_trending

    try:
        result = get_trending(niche, account=account)
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Trending failed: {e}")
        await update.message.reply_text("😅 Trend scan failed. Try again?")


async def cmd_repurpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account, rest = _parse_account(context.args or [])
    content = " ".join(rest) if rest else ""
    if not content:
        await update.message.reply_text(
            "Usage: /repurpose [--hz|--huo] <describe the content>\n"
            "Example: /repurpose --huo OOTD DITL reel that got 5k views showing spring outfits"
        )
        return

    from ingrid.services.repurpose import suggest_repurpose

    try:
        result = suggest_repurpose(content, account=account)
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
    account, rest = _parse_account(context.args or [])
    description = " ".join(rest) if rest else ""
    if not description:
        await update.message.reply_text(
            "Usage: /review [--hz|--huo] <describe how the post did>\n"
            "Example: /review --huo DITL reel got 3k views 150 likes 20 saves but only 5 comments"
        )
        return

    from ingrid.services.review import review_post

    try:
        result = review_post(description, account=account)
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
    account, rest = _parse_account(context.args or [])
    description = " ".join(rest) if rest else ""
    if not description:
        await update.message.reply_text(
            "Usage: /logpost [--hz|--huo] <what you posted>\n"
            "Example: /logpost --huo DITL reel - day 5 library morning"
        )
        return

    from ingrid.services.calendar import log_post

    # Detect format from description
    desc_lower = description.lower()
    if "bold reveal" in desc_lower:
        fmt = "Bold Reveal"
    elif "ditl" in desc_lower or "reel" in desc_lower:
        fmt = "Reel"
    elif "carousel" in desc_lower:
        fmt = "Carousel"
    elif "story" in desc_lower:
        fmt = "Story"
    else:
        fmt = "Post"

    log_post(description, fmt, account=account)
    detected = account or "(auto-detected)"
    await update.message.reply_text(
        f"📝 Logged to @{detected}\nFormat: {fmt}\n{description}"
    )


# ─── Arc-awareness commands ──────────────────────────────────

async def cmd_countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current arc context — days to graduation, act, phase."""
    from ingrid.services.countdown import get_context_summary

    try:
        await update.message.reply_text(
            get_context_summary(), parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.error(f"Countdown failed: {e}")
        await update.message.reply_text("😅 Countdown check failed.")


async def cmd_hero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Plan the graduation hero reel (May 23)."""
    await update.message.reply_text("📸 Planning the hero reel...")

    from core.claude_client import oneshot
    from ingrid.services.countdown import get_context

    ctx = get_context()
    days = ctx["days_to_graduation"]

    prompt = f"""Plan the GRADUATION HERO REEL for @athena_huo — the biggest post of Act 1.

Context:
- Today is {ctx['today']} ({days} days to graduation)
- This is the breakout post of the arc — target >10k views
- Format: DITL or bold reveal, 30-45s
- Grad day: May 23, 2026

PLAYBOOK RULES:
- DO NOT edit this reel on graduation day. Film May 23, edit May 24-25.
- On May 23 itself, post only a simple photo/carousel with minimal caption.
- Hero reel goes up May 24 or 25.
- Shoot more footage than needed: cap fitting, morning getting ready, ceremony, diploma, post-ceremony alone moment.

Produce a COMPLETE hero-reel plan:

🎯 CONCEPT
[One-line high-level concept for the hero reel]

🎬 SHOT LIST (chronological, May 23 filming day)
[Detailed list of every shot to capture — morning, ceremony, diploma, candid moments, the alone moment. 12-18 shots.]

🪝 OPENING HOOK (first 2 seconds)
[Exact spoken line — number/contradiction/uncomfortable truth format]

🗣 VOICEOVER SCRIPT
[Full voiceover text, beat-by-beat, timed to ~35s. Natural pauses. Memorizable beats, not verbatim.]

📝 CAPTION
[DITL-style. "day 31. [observation]. today." — or alternative reflective caption if opting for bold reveal.]

🎵 AUDIO
[Specific track from the playbook shortlist + why]

⏱ POSTING TIMING
[May 24 or 25? Time of day? Why?]

📌 PIN STRATEGY
[When and how to pin. Cross-post to @athena_hz? (Only as polished lookbook, different angle.)]

🔁 @athena_hz VERSION
[The lookbook version — editorial, outfit-first, different caption, different audience.]
"""

    try:
        result = oneshot(
            api_key=config.ANTHROPIC_API_KEY,
            model=config.CLAUDE_MODEL,
            prompt=prompt,
            system_prompt=config.SYSTEM_PROMPT,
            max_tokens=1800,
        )
        await _send_long(update, result)
    except Exception as e:
        log.error(f"Hero plan failed: {e}")
        await update.message.reply_text("😅 Hero reel plan failed. Try again?")


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
        BotCommand("countdown", "Arc status (days to grad, act, phase)"),
        BotCommand("hero", "Plan the graduation hero reel"),
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
    app.add_handler(CommandHandler("countdown", cmd_countdown))
    app.add_handler(CommandHandler("hero", cmd_hero))
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
