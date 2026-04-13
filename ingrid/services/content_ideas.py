"""
Content ideas — strategic, data-backed content suggestions for @athena_hz.
"""

import logging
import random
from datetime import datetime

from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def generate_idea(topic: str = None) -> str:
    """Generate a strategic content idea with hook, format, and reasoning."""
    day = datetime.now().strftime("%A")
    month = datetime.now().strftime("%B %Y")

    # Pick a random pillar if no topic given
    if not topic:
        pillar = random.choice(config.CONTENT_PILLARS)
        topic_hint = f"Content pillar: {pillar['name']} — {pillar['description']}"
    else:
        topic_hint = f"Specific topic requested: {topic}"

    prompt = f"""Generate ONE specific, strategic Instagram content idea for @athena_hz.

Context:
- Today is {day}, {month}
- She's in Ithaca, NY (Cornell campus)
- Account niche: {config.INSTAGRAM_NICHE}
- Audience: {config.INSTAGRAM_AUDIENCE}
- {topic_hint}

Your response MUST include ALL of these:

📌 CONCEPT: [one-line description]
🎬 FORMAT: [Reel / Carousel / Story] + estimated length
🪝 HOOK (first 2 seconds): [exact opening line or visual]
📝 OUTLINE: [3-5 bullet points of the content flow]
📣 CTA: [specific call to action]
🧪 TRIAL REEL?: [Yes/No + reasoning — should this be tested as a trial reel first?]
💡 WHY THIS WORKS: [2 sentences on why this will perform well right now]

Be specific — not "do a fashion reel" but "film a 15-sec outfit transition using the mirror trick with [specific trending audio type]."
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=800,
    )
