"""
Trending — surface trending formats, audios, and content styles on Instagram.
Uses Claude's knowledge + web search context.
"""

import logging
from datetime import datetime

from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def get_trending(niche: str = None) -> str:
    """Get what's trending on Instagram right now for @athena_hz's niche."""
    month = datetime.now().strftime("%B %Y")
    niche_str = niche or config.INSTAGRAM_NICHE

    prompt = f"""What's trending on Instagram Reels RIGHT NOW ({month}) that's relevant for a {niche_str} creator?

Break it down into:

🎵 TRENDING AUDIOS
- 3-4 audios/sounds that are currently viral and relevant
- For each: name, how creators are using it, and whether it fits @athena_hz

📐 TRENDING FORMATS
- 3-4 reel formats/templates that are getting high reach right now
- For each: description, why it works, and a specific idea for @athena_hz

📈 ALGORITHM INSIGHTS
- What Instagram is currently prioritizing (reel length, engagement type, etc.)
- Any recent feature updates creators should use (trial reels, collabs, etc.)

🎯 NICHE-SPECIFIC TRENDS
- What's working specifically in fashion/lifestyle/UGC content right now
- Any seasonal trends to hop on this month

Be specific with audio names and format descriptions — not vague "trending dance" stuff.
If you're not 100% sure an audio is current, say so — better to be honest than outdated.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=1000,
    )
