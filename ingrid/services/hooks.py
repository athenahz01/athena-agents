"""
Hooks — generate A/B hook variations for trial reel testing.
"""

import logging
from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def generate_hooks(topic: str, count: int = 5) -> str:
    """Generate hook variations for A/B testing with trial reels."""
    prompt = f"""Generate {count} different hook variations for an Instagram Reel about: {topic}

Account: @athena_hz ({config.INSTAGRAM_NICHE})
Audience: {config.INSTAGRAM_AUDIENCE}

For EACH hook, provide:
1. The exact opening line (what's said or shown in first 2 seconds)
2. Visual description (what the viewer sees)
3. Hook type (curiosity gap / bold claim / relatable pain / controversy / tutorial promise)
4. Predicted strength (🔥🔥🔥 = strong, 🔥🔥 = good, 🔥 = worth testing)

Make them GENUINELY different approaches — not just rewording the same hook.
At least one should be a "pattern interrupt" style hook (unexpected visual or statement).
At least one should lead with a relatable problem.

End with a recommendation: which 2 hooks to test as trial reels first and why.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=800,
    )
