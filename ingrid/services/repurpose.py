"""
Repurpose — take one piece of content and suggest how to multiply it.
"""

import logging
from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def suggest_repurpose(content_description: str) -> str:
    """Suggest how to repurpose a piece of content across formats."""
    prompt = f"""I have this content: {content_description}

Show me how to repurpose it into multiple Instagram formats for @athena_hz.

For EACH repurposed version:
- Format (Reel / Carousel / Story / Story Series / Post)
- What to change or adapt
- New hook for that format
- Best time to post relative to the original (same day? next day? next week?)

Also suggest:
- Which version to post FIRST for maximum reach
- Which version works as a trial reel test
- Any cross-platform opportunities (TikTok, Pinterest, Threads)

Think like a content strategist maximizing one shoot/idea into a full week of content.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=800,
    )
