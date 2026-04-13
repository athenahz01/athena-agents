"""
Content calendar — generate a strategic weekly posting schedule.
"""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

from core.claude_client import oneshot
from ingrid import config

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


def log_post(description: str, format_type: str, performance: str = ""):
    """Log a post for future calendar optimization."""
    history = _load_history()
    history.append({
        "date": datetime.now().isoformat(),
        "description": description,
        "format": format_type,
        "performance": performance,
    })
    # Keep last 50 entries
    history = history[-50:]
    _save_history(history)


def generate_calendar(days: int = 7) -> str:
    """Generate a content calendar for the next N days."""
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%A, %B %d") for i in range(days)]
    dates_str = "\n".join(f"- {d}" for d in dates)

    # Include recent post history for context
    history = _load_history()
    history_str = ""
    if history:
        recent = history[-10:]
        history_str = "\nRecent posts:\n"
        for h in recent:
            history_str += f"- {h['date'][:10]}: {h['description']} ({h['format']})"
            if h.get("performance"):
                history_str += f" — {h['performance']}"
            history_str += "\n"

    pillars_str = "\n".join(
        f"- {p['name']}: {p['description']} [{', '.join(p['formats'])}]"
        for p in config.CONTENT_PILLARS
    )

    prompt = f"""Create a content calendar for @athena_hz for the next {days} days.

Dates:
{dates_str}

Content pillars:
{pillars_str}

{history_str}

Rules:
- 4-5 posts per week (not every day — quality > quantity)
- Rotate pillars — don't repeat the same type back to back
- Include at least 1 trial reel for testing new ideas
- Specify: day, format, concept, hook, and whether it's a trial reel
- Leave 1-2 days as rest/engagement days (no posting, just stories + engagement)
- Consider the day of week (weekends = lifestyle, weekdays = tips/value content)
- If there's a seasonal/timely hook, prioritize it

Format each day like:
📅 [Day, Date]
[Post / Rest / Trial Reel]
🎬 Format: [type]
💡 Concept: [one line]
🪝 Hook: [opening line]
📝 Notes: [any extra context]

End with a "Week Strategy" summary: what the overall posting rhythm is optimizing for.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=1200,
    )
