"""
Daily proactive check-in — Ingrid's 9am strategic nudge.

This is the CORE Viralt.ai-style feature: instead of only responding to commands,
Ingrid proactively reviews recent activity and surfaces the single most important
thing Athena should focus on today.

Fires from ingrid.__main__ on a schedule (default 9:00 AM ET, configurable).
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
HISTORY_FILE = DATA_DIR / "content_history.json"
INSPO_FILE = DATA_DIR / "inspo_lab.json"
CHECKIN_LOG = DATA_DIR / "checkin_history.json"


def _load_json(path: Path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"Couldn't load {path}: {e}")
    return default


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _days_since_last_post(history: list) -> int | None:
    if not history:
        return None
    try:
        last = datetime.fromisoformat(history[-1]["date"])
        return (datetime.now() - last).days
    except Exception:
        return None


def _format_recent_posts(history: list, n: int = 5) -> str:
    if not history:
        return "No posts logged yet."
    recent = history[-n:]
    lines = []
    for h in recent:
        date = h.get("date", "")[:10]
        desc = h.get("description", "")
        fmt = h.get("format", "")
        perf = h.get("performance", "")
        line = f"- {date}: [{fmt}] {desc}"
        if perf:
            line += f" — {perf}"
        lines.append(line)
    return "\n".join(lines)


def _format_inspo(inspo: list, n: int = 3) -> str:
    if not inspo:
        return "Inspo Lab is empty."
    recent = inspo[-n:]
    return "\n".join(
        f"- {item.get('note', 'saved item')[:100]}" for item in recent
    )


def build_checkin() -> str:
    """Build today's proactive check-in message."""
    now = datetime.now()
    day = now.strftime("%A")
    date_str = now.strftime("%B %d")

    history = _load_json(HISTORY_FILE, [])
    inspo = _load_json(INSPO_FILE, [])
    days_since = _days_since_last_post(history)
    posts_this_week = sum(
        1
        for h in history
        if "date" in h
        and (now - datetime.fromisoformat(h["date"])).days <= 7
    )

    # Situational flags for the prompt
    signals = []
    if days_since is None:
        signals.append("No posts logged yet — help her start")
    elif days_since >= 4:
        signals.append(f"⚠️ {days_since} days since last post — momentum slipping")
    elif days_since <= 1:
        signals.append("Just posted — good moment for engagement push, not new post")

    if posts_this_week < 2:
        signals.append(f"Only {posts_this_week} posts this week — below 4-5/week target")
    elif posts_this_week >= 5:
        signals.append(f"{posts_this_week} posts this week — strong cadence")

    if day in ("Saturday", "Sunday"):
        signals.append("Weekend — lifestyle content performs better")
    else:
        signals.append("Weekday — value/tip content performs better")

    signals_str = "\n".join(f"- {s}" for s in signals)

    pillars = "\n".join(
        f"- {p['name']}: {p['description']}" for p in config.CONTENT_PILLARS
    )

    prompt = f"""It's {day}, {date_str}. Give Athena her daily content check-in for @athena_hz.

SITUATIONAL SIGNALS:
{signals_str}

RECENT POSTS:
{_format_recent_posts(history)}

RECENT INSPO SAVED:
{_format_inspo(inspo)}

CONTENT PILLARS:
{pillars}

Your job: deliver a SHORT, strategic morning brief. Structure EXACTLY like this, using these headers:

🎯 TODAY'S MOVE
[ONE specific thing to do today — post X, film Y, or engage instead of posting. Be concrete. Include format + hook if it's a post.]

📊 WHY
[1-2 sentences — algorithm logic, timing, or pattern from her data]

🔥 QUICK HIT
[ONE bite-sized tip she can execute in under 10 minutes — could be: story prompt, comment strategy, trending audio to save, caption tweak]

💭 WATCHING FOR
[ONE thing to pay attention to this week — a trend forming, a content pillar she's neglecting, an opportunity]

Rules:
- No fluff. No "good morning!" No emoji spam.
- Be specific — not "post a reel," but "film 15-sec transition with the [specific trend] audio"
- If she's behind on posting, push her gently. If she's on track, optimize.
- Under 200 words total.
"""

    response = oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=600,
    )

    # Log this check-in
    log_entry = {
        "date": now.isoformat(),
        "signals": signals,
        "posts_this_week": posts_this_week,
        "days_since_last_post": days_since,
    }
    history_log = _load_json(CHECKIN_LOG, [])
    history_log.append(log_entry)
    history_log = history_log[-60:]  # keep 60 days
    _save_json(CHECKIN_LOG, history_log)

    header = f"📸 <b>Ingrid — {day} Check-In</b>\n\n"
    return header + response
