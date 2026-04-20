"""
Daily proactive check-in — Ingrid's 9am strategic nudge.

Viralt-style daily manager mode, now arc-aware: factors in days-until-graduation,
current phase (establish/open loop/land moment), and the primary growth account
(@athenahuo) vs portfolio account (@athena_hz).
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from core.claude_client import oneshot
from ingrid import config
from ingrid.services.countdown import get_context, current_pillars

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


def _days_since_last_post(history: list, account: str = None) -> int | None:
    relevant = [
        h for h in history if not account or h.get("account") == account
    ] if account else history
    if not relevant:
        return None
    try:
        last = datetime.fromisoformat(relevant[-1]["date"])
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
        acct = h.get("account", "")
        perf = h.get("performance", "")
        line = f"- {date} [{acct or '?'}] [{fmt}] {desc}"
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
    """Build today's proactive check-in. Arc-aware + two-account aware."""
    now = datetime.now()
    day = now.strftime("%A")
    date_str = now.strftime("%B %d")

    ctx = get_context()
    history = _load_json(HISTORY_FILE, [])
    inspo = _load_json(INSPO_FILE, [])

    # Cadence checks per account
    huo_days_since = _days_since_last_post(history, account="athenahuo")
    hz_days_since = _days_since_last_post(history, account="athena_hz")
    huo_this_week = sum(
        1
        for h in history
        if h.get("account") == "athenahuo"
        and "date" in h
        and (now - datetime.fromisoformat(h["date"])).days <= 7
    )
    hz_this_week = sum(
        1
        for h in history
        if h.get("account") == "athena_hz"
        and "date" in h
        and (now - datetime.fromisoformat(h["date"])).days <= 7
    )

    # Signals
    signals = []

    # Arc-specific signals
    if ctx["act"] == "act_1":
        signals.append(f"🎯 ACT 1 · {ctx['phase']} · {ctx['days_to_graduation']} days to graduation")
        signals.append(f"Phase focus: {ctx['phase_focus']}")
    elif ctx["act"] == "bridge":
        signals.append("🌉 BRIDGE period — packing/final Ithaca content, no countdown")
    elif ctx["act"] == "moving_week":
        signals.append("📦 MOVING WEEK — apartment arrival, first NYC days")
    elif ctx["act"] == "act_2":
        signals.append(f"🗽 ACT 2 · NYC era")

    # Graduation day special
    if ctx["days_to_graduation"] == 0:
        signals.append("⭐ GRADUATION DAY. Post simple photo/carousel with minimal caption today. Shoot everything. DO NOT edit hero reel today — edit May 24-25.")

    # Countdown suffix to use in today's caption
    if ctx["countdown_suffix"]:
        signals.append(f"Caption suffix: \"{ctx['countdown_suffix']}\"")

    # @athenahuo cadence (5-6/week target)
    if huo_days_since is None:
        signals.append("@athenahuo: no posts logged yet")
    elif huo_days_since >= 2 and ctx["act"] == "act_1":
        signals.append(f"⚠️ @athenahuo: {huo_days_since} days silent — act 1 needs near-daily cadence")
    if ctx["act"] == "act_1" and huo_this_week < 4:
        signals.append(f"@athenahuo: only {huo_this_week} posts this week — target 5-6")

    # @athena_hz cadence (1-2/week target)
    if hz_this_week > 2:
        signals.append(f"⚠️ @athena_hz: {hz_this_week} posts this week — exceeds 1-2/week cap")

    # Day-of-week
    if day == "Sunday":
        signals.append("Sunday — @athenahuo prime lifestyle window 7-9pm ET. Weekly review day.")
    elif day in ("Saturday", "Sunday"):
        signals.append("Weekend — lifestyle/slow-living performs")
    else:
        signals.append("Weekday — post 7-9am ET or 7-9pm ET")

    signals_str = "\n".join(f"- {s}" for s in signals)
    pillars = "\n".join(
        f"- {p.get('name', '')} ({p.get('weight', 0)}%): {p.get('description', '')}"
        for p in current_pillars()
    )

    prompt = f"""It's {day}, {date_str}. Give Athena her daily Ingrid check-in.

SITUATIONAL SIGNALS:
{signals_str}

RECENT POSTS (both accounts):
{_format_recent_posts(history)}

RECENT INSPO SAVED:
{_format_inspo(inspo)}

CURRENT ACT'S CONTENT PILLARS:
{pillars}

Your job: deliver a SHORT, strategic morning brief. Structure EXACTLY like this, using these headers:

🎯 TODAY'S MOVE
[Specify WHICH ACCOUNT. Then ONE specific action — if @athenahuo, include format (DITL/bold reveal), hook (one of: number/contradiction/uncomfortable truth), and the countdown suffix if Act 1. If @athena_hz, only suggest if week's 1-2 cap allows. Be CONCRETE.]

📊 WHY
[1-2 sentences grounded in the arc, the phase, the KPI priorities (saves/shares > likes), or her data]

🔥 QUICK HIT
[ONE under-10-min tactical thing — could be: a caption draft, a specific hook line, a b-roll shot to grab today, a trending audio to save, engagement move]

💭 WATCHING FOR
[ONE thing to track this week — phase milestone, cadence risk, pillar she's neglected, arc moment coming up]

Rules:
- No fluff. No "good morning!" No emoji spam.
- If @athenahuo post today, write an example hook using number/contradiction/uncomfortable truth format.
- If Act 1, include the countdown ("X to go.") in any caption examples.
- Never suggest "teach 5 tips" style content for @athenahuo.
- Under 220 words.
"""

    response = oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=700,
    )

    # Log this check-in
    log_entry = {
        "date": now.isoformat(),
        "act": ctx["act"],
        "phase": ctx["phase"],
        "days_to_graduation": ctx["days_to_graduation"],
        "signals": signals,
        "huo_posts_this_week": huo_this_week,
        "hz_posts_this_week": hz_this_week,
    }
    history_log = _load_json(CHECKIN_LOG, [])
    history_log.append(log_entry)
    history_log = history_log[-90:]
    _save_json(CHECKIN_LOG, history_log)

    header = f"📸 <b>Ingrid — {day} Check-In</b>\n"
    if ctx["days_to_graduation"] > 0 and ctx["act"] in ("act_1",):
        header += f"<i>{ctx['days_to_graduation']} to go · {ctx['phase']}</i>\n\n"
    else:
        header += f"<i>{ctx['phase']}</i>\n\n"
    return header + response
