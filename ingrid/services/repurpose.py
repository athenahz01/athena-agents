"""
Repurpose — multiply one piece of content. Respects the two-account separation rule.
"""

import logging
from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def suggest_repurpose(content_description: str, account: str = None) -> str:
    """Suggest repurposing paths. NEVER suggests cross-posting between the two accounts."""
    account = account or config.DEFAULT_ACCOUNT

    prompt = f"""Athena has this content: {content_description}
Origin account: @{account}

Show how to multiply it into multiple formats — STAYING ON @{account} unless it's graduation day content (the only cross-account exception).

HARD RULE: Never suggest reposting content from @athenahuo to @athena_hz or vice versa.
- @athena_hz = editorial fashion portfolio. 1-2 posts/week cap.
- @athenahuo = story-driven, voiceover DITL, 5-6/week + stories.

For EACH repurposed version:
- Target format (Reel / Carousel / Story / Story Series)
- What changes or adapts for that format
- New hook (playbook-compliant if @athenahuo: number/contradiction/uncomfortable truth)
- Caption direction
- Best posting timing (hours/days after original)

Also:
- Which version posts FIRST for max reach
- Which works as a trial reel test
- Cross-platform spillover: TikTok? Pinterest? Threads? (different than cross-account)

Think like a content director maximizing one shoot into a week of posts.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=900,
    )
