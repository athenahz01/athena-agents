"""
Viral Scan — synthesize what's working in Athena's niche right now.

Viralt.ai advertises "analyzes comparable viral videos and identifies hooks
that work within a creator's niche." Since scraping Instagram programmatically
violates ToS, we use Claude to synthesize viral pattern analysis based on:
- Her specific niche & audience
- Her content pillars
- Any user-pasted reference (link or description of a viral reel)

Two modes:
- `/viral` → general niche viral scan
- `/viral <url or description>` → deep-dive on a specific reel/trend
"""

import logging
from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def scan_niche() -> str:
    """General viral scan for @athena_hz's niche."""
    pillars = ", ".join(p["name"] for p in config.CONTENT_PILLARS)

    prompt = f"""Give Athena a VIRAL SCAN report for @athena_hz.

Account: fashion, lifestyle, UGC brand collaborations
Audience: College-age women, fashion/lifestyle/Asian-American, bilingual EN/CN
Content pillars: {pillars}

Synthesize the MOST VIRAL patterns in her niche right now. Structure exactly:

🔥 HOOK FORMULAS WINNING RIGHT NOW
[List 3 specific hook patterns working in her niche — with example opening lines she could adapt. Format: "PATTERN: [name] — EXAMPLE: [line]"]

🎬 FORMAT TRENDS
[2-3 format patterns — e.g. "POV storytelling carousels with 8+ slides," "silent Reels with text overlay only," "before/after transitions with outfit sound"]

🎵 AUDIO DIRECTION
[What type of audio is winning — slow sentimental, chaotic trending, silent, voiceover. Be specific about the vibe, not song names (those change fast).]

📊 PERFORMANCE PATTERN
[ONE insight about what Instagram is boosting right now — e.g., "Carousels >5 slides getting 2x reach," "Reels under 15 sec outperforming longer ones"]

🎯 ATHENA'S ANGLE
[Given her niche + audience, the ONE specific concept she should test this week. Include: format + hook + why it hits her audience specifically.]

Rules:
- No generic advice. Everything must be niche-specific.
- If she can watch 5 creators in her niche tonight and spot these patterns, you did it right.
- Under 400 words. Punchy.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=1000,
    )


def analyze_reference(reference: str) -> str:
    """Deep-dive analysis on a user-provided reel/trend reference."""
    prompt = f"""Athena shared this as a reference to analyze:

"{reference}"

Her account: @athena_hz — {config.INSTAGRAM_NICHE}
Audience: {config.INSTAGRAM_AUDIENCE}

Break it down for her. Structure exactly:

🔬 WHY IT'S WORKING
[2-3 sentences on the specific elements that make this go viral — hook mechanism, pacing, CTA, emotion, format choice]

🎯 THE BORROWABLE ELEMENT
[ONE specific thing she can extract and adapt — NOT "do something similar" but "open with the same X pattern" or "use the same caption structure"]

✍️ HER VERSION
[A concrete concept for her account using that borrowable element. Include:
- Format (Reel / Carousel / Story)
- Hook (first 2 sec, exact)
- Structure (3-4 beats)
- CTA
- Why this translates to HER audience specifically]

⚠️ DON'T COPY
[ONE thing about the reference that WOULDN'T work for her — wrong audience, off-brand, saturated trend, etc.]

Under 350 words. Be specific.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=900,
    )
