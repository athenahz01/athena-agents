"""
Review — analyze post performance and suggest strategic adjustments.
"""

import logging
from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def review_post(description: str) -> str:
    """Analyze a post's performance and suggest what to do next."""
    prompt = f"""Athena is describing how her latest Instagram post performed: {description}

Analyze this and give her:

📊 PERFORMANCE ASSESSMENT
- Is this good, average, or underperforming? (relative to a ~5K-20K follower fashion/lifestyle account)
- What metric matters most for this type of content?

🔍 WHY IT PERFORMED THIS WAY
- 2-3 specific reasons (hook strength, timing, format choice, topic relevance)
- Be honest — if the content had issues, say so directly

🔄 WHAT TO DO NEXT
- Should she repurpose this content? How?
- Should she double down on this topic/format or pivot?
- Specific adjustments for the next similar post

🧪 TEST SUGGESTION
- One specific trial reel idea based on what she learned from this post

Be data-minded and strategic. No cheerleading — give her real analysis.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=800,
    )
