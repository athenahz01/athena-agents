"""
Content ideas — arc-aware, playbook-compliant content suggestions.
"""

import logging
import random
from datetime import datetime

from core.claude_client import oneshot
from ingrid import config
from ingrid.services.countdown import get_context, current_pillars

log = logging.getLogger(__name__)


def generate_idea(topic: str = None, account: str = None) -> str:
    """Generate a specific content idea. Arc-aware for @athenahuo."""
    account = account or config.DEFAULT_ACCOUNT
    acct = config.account_config(account)
    ctx = get_context()
    day = datetime.now().strftime("%A")

    pillars = current_pillars()

    # Pick a pillar weighted by the % in strategy.json
    if pillars and not topic:
        weights = [p.get("weight", 1) for p in pillars]
        pillar = random.choices(pillars, weights=weights, k=1)[0]
        topic_hint = f"Content pillar: {pillar['name']} — {pillar['description']}"
    elif topic:
        topic_hint = f"Specific topic requested: {topic}"
    else:
        topic_hint = "No pillar specified — pick one that fits today's phase"

    # Account-specific constraints
    if account == "athenahuo":
        account_constraints = f"""ACCOUNT: @athenahuo (growth / story-driven)
ACT: {ctx['act']} — {ctx['phase']}
DAYS TO GRADUATION: {ctx['days_to_graduation']}
COUNTDOWN SUFFIX FOR CAPTION: "{ctx['countdown_suffix'] or '(none — post-arc)'}"

REQUIRED FORMAT: Voiceover DITL (unless explicitly suggesting bold reveal).
4-part structure:
  0-5s: Face to camera. HOOK.
  5-8s: Setup line.
  8-30s: B-roll with voiceover. Timestamps on beats.
  30-35s: Closing + countdown overlay.

Hook MUST be one of: number / contradict a belief / uncomfortable truth.
Caption MUST follow DITL structure: "day [x]. [observation]. [countdown]."
Hashtags = 5 in first comment (2 niche + 2 mid + 1 broad)."""
    else:
        account_constraints = f"""ACCOUNT: @athena_hz (portfolio — editorial fashion)
Cadence: 1-2 posts/week max. Suggest only if fits weekly cap.
Tone: Editorial, polished, brand-deal-ready.
No voiceover DITL, no emotional content, no NYC content, no engineering content."""

    prompt = f"""Generate ONE specific, strategic Instagram content idea.

{account_constraints}

Today is {day}. {topic_hint}

Required output (use these exact headers):

📌 CONCEPT: [one-line description]
📱 ACCOUNT: @{account}
🎬 FORMAT: [Reel / Carousel / Story / Bold Reveal] + estimated length
🪝 HOOK (first 2 seconds): [exact spoken/written opening — playbook-compliant]
📝 OUTLINE: [3-5 bullet points of the content flow — include voiceover beats + b-roll for DITL]
📝 CAPTION: [draft caption following rules for this account]
🎵 AUDIO: [specific audio suggestion from playbook list or rationale]
📣 CTA: [playbook rule — @athenahuo rarely has CTAs; @athena_hz can have one]
🧪 TRIAL REEL?: [Yes/No + why]
💡 WHY THIS WORKS: [2 sentences — arc fit, algorithm logic, audience fit]

Be SPECIFIC — not "do a fashion reel," but "film 15s DITL: 7am coffee → library walk → 2pm library frustration → 8pm sunset over the lake. Opening line: 'I woke up at 6:48. 23 days left.'"
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=1000,
    )
