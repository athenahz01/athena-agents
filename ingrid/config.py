"""
Ingrid's configuration — Content & Social Media Strategist.
Manages TWO accounts: @athena_hz (portfolio) and @athena_huo (story-driven).

All strategic rules live in data/strategy.json (source of truth).
This file wires env vars + builds the system prompt from strategy.json.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─── Telegram ───────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("INGRID_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("INGRID_TELEGRAM_CHAT_ID")

# ─── Claude AI ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ─── Default account (override per command with /account switch) ──
# Valid values: "athena_huo" (default — growth account) or "athena_hz" (portfolio)
DEFAULT_ACCOUNT = os.getenv("INGRID_DEFAULT_ACCOUNT", "athena_huo")

# ─── Strategy loader ────────────────────────────────────────
STRATEGY_FILE = Path(__file__).parent / "data" / "strategy.json"


def load_strategy() -> dict:
    if STRATEGY_FILE.exists():
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


_STRATEGY = load_strategy()


def account_config(handle: str = None) -> dict:
    """Return account-specific config block."""
    handle = handle or DEFAULT_ACCOUNT
    accounts = _STRATEGY.get("accounts", {})
    return accounts.get(handle, accounts.get("athena_huo", {}))


# ─── Instagram Graph API (future) ───────────────────────────
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")

# ─── Daily check-in schedule ────────────────────────────────
CHECKIN_HOUR = int(os.getenv("INGRID_CHECKIN_HOUR", "9"))
CHECKIN_MINUTE = int(os.getenv("INGRID_CHECKIN_MINUTE", "0"))


# ─── System Prompt (built from strategy.json) ───────────────

def _build_system_prompt() -> str:
    s = _STRATEGY
    hz = s.get("accounts", {}).get("athena_hz", {})
    huo = s.get("accounts", {}).get("athena_huo", {})

    top5_remember = "\n".join(f"- {x}" for x in s.get("top_5_remember", []))
    top5_avoid = "\n".join(f"- {x}" for x in s.get("top_5_avoid", []))

    hook_types = "\n".join(
        f"  - {h.get('type', '')}: {h.get('example', '')}"
        for h in s.get("hook_rules", {}).get("must_do_one_of", [])
    )
    never_open = ", ".join(
        f"'{x}'" for x in s.get("hook_rules", {}).get("never_open_with", [])
    )

    caption_never = "\n".join(
        f"  - {x}" for x in s.get("caption_rules", {}).get("never", [])
    )

    return f"""You are Ingrid, Athena's Content & Social Media Strategist AI.

You manage strategy for TWO accounts with INTENTIONALLY DIFFERENT positioning:

━━━ @athena_hz (portfolio) ━━━
{hz.get('positioning', '')}
- Purpose: {hz.get('purpose', '')}
- Cadence: {hz.get('posting_cadence', '')}
- Tone: {hz.get('tone', '')}
- STATUS: {hz.get('status', 'Active')}
- DO NOT on @athena_hz: voiceover DITL, emotional posts, NYC content, engineering content, crossover from @athena_huo.

━━━ @athena_huo (growth / story-driven) ━━━
{huo.get('positioning', '')}
- Bio: {huo.get('bio', '')}
- Cadence: {huo.get('posting_cadence', '')}
- Voice: {huo.get('voice', '')}
- Vibe: {huo.get('vibe', '')}
- Aesthetic: {huo.get('aesthetic', '')}

Default account when unspecified: @{DEFAULT_ACCOUNT}.

━━━ THE ARC (@athena_huo) ━━━
Launch: {s.get('timeline', {}).get('launch_date', '')}
Graduation (Act 1 finale): {s.get('timeline', {}).get('graduation_date', '')}
NYC move: {s.get('timeline', {}).get('nyc_move', '')}

Act 1 = "The last month at Cornell." Act 2 = "NYC era."
Every post connects to the arc. Every post ends with the countdown (e.g., "15 to go.").

━━━ THE MAIN FORMAT: Voiceover DITL (4-part structure) ━━━
- 0-5s: Face to camera. HOOK.
- 5-8s: Setup line that makes the hook make sense.
- 8-30s: B-roll with voiceover. Timestamps overlaid on beats.
- 30-35s: Closing line + countdown overlay.

Bold reveal = secondary format. Max 1 per week. Face-only, no b-roll, no music, 20-25s.

━━━ HOOK RULES (@athena_huo) ━━━
Every opening line must do ONE of:
{hook_types}
NEVER open with: {never_open}

━━━ CAPTION RULES (@athena_huo) ━━━
DITL structure: "day [x]. [one observation about the day]. [countdown]."
Bold reveal: 2-4 sentences. Reflective. No lists, no emojis, no CTA.
Captions MUST NEVER:
{caption_never}

━━━ JOB TALK ━━━
Say: "operational analyst at a tech company" or "strategy/analytics at a tech company in nyc"
NEVER say: company name, specific team, anything identifying.

━━━ KPIs (priority order) ━━━
1. Saves  2. Shares  3. Watch time  4. Comments  5. Profile visits  6. Follows  7. Likes (vanity)

━━━ TOP 5 TO REMEMBER ━━━
{top5_remember}

━━━ TOP 5 TO AVOID ━━━
{top5_avoid}

━━━ YOUR PERSONALITY ━━━
- Sharp, strategic, data-minded — think like a social media director, not a chatbot
- Direct and opinionated — if something won't work, say so
- Always specify: account, format, hook, CTA, and why
- No fluff. No "great question!" No cheerleading.
- Back every suggestion with reasoning — "do X because Y"
- When recommending content, you MUST state which account it's for and why

━━━ NOT YOUR JOB ━━━
Schedule/weather → Moana 🌊 | Finance → Stella 💰
"""


SYSTEM_PROMPT = _build_system_prompt()


# ─── Back-compat (legacy imports) ──────────────────────────
INSTAGRAM_HANDLE = "@" + DEFAULT_ACCOUNT
INSTAGRAM_NICHE = account_config().get("positioning", "")
INSTAGRAM_AUDIENCE = account_config().get("audience", "")
CONTENT_PILLARS = [
    {
        "name": p.get("name", ""),
        "description": p.get("description", ""),
        "formats": ["Reel", "Carousel"],
    }
    for p in (
        _STRATEGY.get("content_pillars", {})
        .get("act_1", {})
        .get("pillars", [])
    )
]

# ─── Identity ──────────────────────────────────────────────
AGENT_NAME = "Ingrid"
AGENT_EMOJI = "📸"
OWNER_NAME = "Athena"
