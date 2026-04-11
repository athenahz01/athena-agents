"""
Deadlines & reminders — persistent tracker for Athena's projects.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

log = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent.parent / "data" / "deadlines.json"


def _load() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"deadlines": [], "reminders": []}


def _save(data: dict):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_upcoming_deadlines(days_ahead: int = 14) -> dict:
    """Get deadlines within the next N days + active reminders."""
    data = _load()
    now = datetime.now()
    cutoff = now + timedelta(days=days_ahead)

    upcoming = []
    for d in data.get("deadlines", []):
        try:
            deadline_date = datetime.fromisoformat(d["date"])
            if now <= deadline_date <= cutoff:
                upcoming.append({**d, "days_left": (deadline_date - now).days})
        except (ValueError, KeyError):
            continue

    upcoming.sort(key=lambda x: x["days_left"])
    return {"deadlines": upcoming, "reminders": data.get("reminders", [])}


def add_reminder(text: str):
    """Add a quick reminder."""
    data = _load()
    data.setdefault("reminders", []).append({
        "text": text,
        "added": datetime.now().isoformat(),
    })
    _save(data)


def add_deadline(title: str, date_str: str, category: str = "general"):
    """Add a deadline (date_str = YYYY-MM-DD)."""
    data = _load()
    data["deadlines"].append({
        "title": title,
        "date": date_str,
        "category": category,
    })
    _save(data)


def clear_reminders():
    """Clear all reminders."""
    data = _load()
    data["reminders"] = []
    _save(data)
