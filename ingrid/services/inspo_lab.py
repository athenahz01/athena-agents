"""
Inspo Lab — persistent library of inspiration, ideas, references.

Viralt.ai calls theirs "Inspo Lab" — auto-saves content breakdowns and ideas.
Ours lets Athena save ANY inspiration via /save, then browse or search it later.

Each entry stores:
- note (user's text / paste / link)
- tags (auto-extracted by Claude or manual)
- breakdown (if the saved item is a URL to a reel/post, Claude explains why it works)
- date
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path

from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)

INSPO_FILE = Path(__file__).parent.parent / "data" / "inspo_lab.json"


def _load() -> list:
    if INSPO_FILE.exists():
        try:
            with open(INSPO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"Couldn't load inspo: {e}")
    return []


def _save(items: list):
    INSPO_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INSPO_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


def _extract_url(text: str) -> str | None:
    m = re.search(r"https?://[^\s]+", text)
    return m.group(0) if m else None


def save_item(note: str, auto_analyze: bool = True) -> str:
    """Save an inspiration item. If text contains a URL, optionally analyze why it works."""
    items = _load()
    url = _extract_url(note)

    entry = {
        "id": len(items) + 1,
        "date": datetime.now().isoformat(),
        "note": note,
        "url": url,
        "breakdown": None,
        "tags": [],
    }

    # Auto-analyze + tag via Claude
    if auto_analyze:
        try:
            analysis = _analyze(note, url)
            entry["breakdown"] = analysis.get("breakdown", "")
            entry["tags"] = analysis.get("tags", [])
        except Exception as e:
            log.warning(f"Inspo analysis failed: {e}")

    items.append(entry)
    _save(items)

    # Build confirmation message
    confirm = f"💾 <b>Saved to Inspo Lab #{entry['id']}</b>\n\n"
    confirm += f"<i>{note[:200]}</i>\n"
    if entry["tags"]:
        confirm += f"\n🏷 Tags: {', '.join(entry['tags'])}\n"
    if entry["breakdown"]:
        confirm += f"\n🔍 <b>Why it works:</b>\n{entry['breakdown']}"
    return confirm


def _analyze(note: str, url: str | None) -> dict:
    """Ask Claude to break down the inspo + extract tags."""
    url_context = f"\nURL referenced: {url}" if url else ""

    prompt = f"""Athena just saved this to her content Inspo Lab:

"{note}"{url_context}

Her account: @athena_hz — {config.INSTAGRAM_NICHE}
Audience: {config.INSTAGRAM_AUDIENCE}

Do TWO things:

1. BREAKDOWN: If she's saving a reel/post/trend, explain in 2-3 sentences WHY this works and what ONE specific element she should borrow. If it's just a note/idea, skip breakdown and write one strategic observation instead.

2. TAGS: Extract 2-4 short tags (lowercase, one word each) that describe what this is about. Examples: hook, transition, ootd, ugc, trending-audio, carousel, cta, bilingual.

Respond in this EXACT format:

BREAKDOWN: [your text]
TAGS: tag1, tag2, tag3
"""

    response = oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=400,
    )

    result = {"breakdown": "", "tags": []}

    for line in response.splitlines():
        if line.startswith("BREAKDOWN:"):
            result["breakdown"] = line.replace("BREAKDOWN:", "").strip()
        elif line.startswith("TAGS:"):
            tags = line.replace("TAGS:", "").strip()
            result["tags"] = [
                t.strip().lower() for t in tags.split(",") if t.strip()
            ][:4]

    return result


def list_recent(n: int = 10) -> str:
    """Return a formatted list of the most recent inspo items."""
    items = _load()
    if not items:
        return "💾 Your Inspo Lab is empty. Save your first inspiration with /save <note or link>"

    recent = items[-n:][::-1]  # newest first
    lines = [f"💾 <b>Inspo Lab</b> ({len(items)} total, showing last {len(recent)})\n"]

    for item in recent:
        date = item.get("date", "")[:10]
        note_short = item.get("note", "")[:120]
        if len(item.get("note", "")) > 120:
            note_short += "..."

        lines.append(f"<b>#{item['id']}</b> — {date}")
        lines.append(f"<i>{note_short}</i>")
        if item.get("tags"):
            lines.append(f"🏷 {', '.join(item['tags'])}")
        lines.append("")

    lines.append("💡 /inspo search &lt;word&gt; to filter · /inspo &lt;id&gt; for full breakdown")
    return "\n".join(lines)


def search(query: str, limit: int = 10) -> str:
    """Search inspo by keyword in note, tags, or breakdown."""
    items = _load()
    q = query.lower().strip()

    matches = [
        item
        for item in items
        if q in item.get("note", "").lower()
        or q in " ".join(item.get("tags", [])).lower()
        or q in (item.get("breakdown") or "").lower()
    ]

    if not matches:
        return f"🔍 No inspo found matching '<b>{query}</b>'"

    recent = matches[-limit:][::-1]
    lines = [f"🔍 <b>Inspo matching '{query}'</b> ({len(matches)} results)\n"]

    for item in recent:
        date = item.get("date", "")[:10]
        lines.append(f"<b>#{item['id']}</b> — {date}")
        lines.append(f"<i>{item.get('note', '')[:150]}</i>")
        if item.get("tags"):
            lines.append(f"🏷 {', '.join(item['tags'])}")
        lines.append("")

    return "\n".join(lines)


def get_by_id(item_id: int) -> str:
    """Return full detail for one inspo entry."""
    items = _load()
    match = next((item for item in items if item.get("id") == item_id), None)

    if not match:
        return f"🔍 No inspo #{item_id} found."

    lines = [f"💾 <b>Inspo #{match['id']}</b>"]
    lines.append(f"📅 {match.get('date', '')[:10]}")
    lines.append("")
    lines.append(f"<b>Note:</b>\n{match.get('note', '')}")

    if match.get("url"):
        lines.append(f"\n🔗 {match['url']}")
    if match.get("tags"):
        lines.append(f"\n🏷 {', '.join(match['tags'])}")
    if match.get("breakdown"):
        lines.append(f"\n🔍 <b>Breakdown:</b>\n{match['breakdown']}")

    return "\n".join(lines)


def delete(item_id: int) -> str:
    """Remove an inspo item."""
    items = _load()
    before = len(items)
    items = [item for item in items if item.get("id") != item_id]

    if len(items) == before:
        return f"🔍 No inspo #{item_id} found."

    _save(items)
    return f"🗑 Deleted inspo #{item_id}."
