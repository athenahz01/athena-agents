"""
Content calendar — arc-aware weekly plan for @athenahuo (+ optional @athena_hz slots).
"""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

from core.claude_client import oneshot
from ingrid import config
from ingrid.services.countdown import get_context, current_pillars

log = logging.getLogger(__name__)

HISTORY_FILE = Path(__file__).parent.parent / "data" / "content_history.json"


def _load_history() -> list:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_history(history: list):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def log_post(description: str, format_type: str, account: str = None, performance: str = ""):
    """Log a post. Account defaults to DEFAULT_ACCOUNT but is inferred from description if possible."""
    if not account:
        desc_lower = description.lower()
        if "@athena_hz" in desc_lower or "athena_hz" in desc_lower:
            account = "athena_hz"
        elif "@athenahuo" in desc_lower or "athenahuo" in desc_lower:
            account = "athenahuo"
        else:
            account = config.DEFAULT_ACCOUNT

    history = _load_history()
    history.append({
        "date": datetime.now().isoformat(),
        "account": account,
        "description": description,
        "format": format_type,
        "performance": performance,
    })
    history = history[-100:]  # keep last 100
    _save_history(history)


def generate_calendar(days: int = 7) -> str:
    """Arc-aware content calendar."""
    today = datetime.now()
    ctx = get_context(today.date())
    dates = []
    for i in range(days):
        d = today + timedelta(days=i)
        d_ctx = get_context(d.date())
        suffix = d_ctx.get("countdown_suffix") or ""
        dates.append(f"- {d.strftime('%A, %B %d')} ({suffix})".rstrip(" ()"))
    dates_str = "\n".join(dates)

    history = _load_history()
    history_str = ""
    if history:
        recent = history[-10:]
        history_str = "\nRecent posts:\n"
        for h in recent:
            history_str += f"- {h['date'][:10]} [@{h.get('account', '?')}]: {h['description']} ({h['format']})"
            if h.get("performance"):
                history_str += f" — {h['performance']}"
            history_str += "\n"

    pillars_str = "\n".join(
        f"- {p.get('name', '')} ({p.get('weight', 0)}%): {p.get('description', '')}"
        for p in current_pillars()
    )

    prompt = f"""Build a content calendar for the next {days} days.

ARC CONTEXT:
- Current act: {ctx['act']} — {ctx['phase']}
- Phase focus: {ctx['phase_focus']}
- Days to graduation: {ctx['days_to_graduation']}

DATES (with caption countdown suffix where applicable):
{dates_str}

CURRENT PILLARS (weighted):
{pillars_str}

{history_str}

RULES:
- @athenahuo: 5-6 posts this week (near-daily during Act 1 Phase 3). Include at least one bold reveal at most.
- @athena_hz: 1-2 posts max, editorial only, don't exceed cap.
- Every @athenahuo post is voiceover DITL (35s) unless flagged as bold reveal.
- Every @athenahuo caption ends with the countdown suffix for THAT day.
- Rotate pillars per their weights (Last Times 40%, Aesthetic Daily Life 30%, Grad Prep 20%, Moat 10%).
- Weekday posts: 7-9am or 7-9pm ET. Weekend: 10-11am or 8-10pm ET. Sunday: 7-9pm ET peak.

Format each day EXACTLY like:
📅 [Day, Date] ({{countdown suffix}})
📱 Account: @athenahuo OR @athena_hz OR REST/Stories-only
🎬 Format: [DITL Reel / Bold Reveal / Carousel / Post / REST]
💡 Concept: [one line — specific, arc-connected]
🪝 Hook: [exact opening line — number/contradiction/uncomfortable truth for @athenahuo]
📝 Caption: ["day N. [observation]. {{countdown}}." for @athenahuo]
⏰ Post at: [time in ET]

End with a "Week Strategy" paragraph: how this week moves the arc, which KPIs you're optimizing for, and what success looks like by Sunday.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=1500,
    )
