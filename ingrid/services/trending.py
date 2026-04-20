"""
Trending — surface trending formats + audios, filtered through the playbook.
"""

import logging
from datetime import datetime

from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def get_trending(niche: str = None, account: str = None) -> str:
    """What's trending, framed for the target account."""
    account = account or config.DEFAULT_ACCOUNT
    acct = config.account_config(account)
    month = datetime.now().strftime("%B %Y")

    # Pull the playbook's current audio list
    strategy = config.load_strategy()
    current_audio = strategy.get("trending_audio_april_2026", [])
    audio_lines = "\n".join(
        f"- \"{a.get('title', '')}\" {'by ' + a.get('artist', '') if a.get('artist') else ''} — {a.get('note', '')}"
        for a in current_audio
    )

    prompt = f"""What's trending on Instagram Reels RIGHT NOW ({month}) that's relevant for @{account}?

Account positioning: {acct.get('positioning', '')}
Aesthetic: {acct.get('aesthetic', '')}

PLAYBOOK AUDIO SHORTLIST (April 2026, refresh monthly):
{audio_lines}

Produce:

🎵 AUDIO FIT
[Pick 2-3 from the playbook shortlist that fit THIS account right now. For each: one reel idea using it.]

📐 FORMATS GAINING REACH
[3 reel/carousel formats that are performing right now in {acct.get('positioning', '')} niche. Be specific — format, pacing, what makes it pop.]

📈 ALGORITHM SIGNAL
[What Instagram is currently rewarding — prioritize saves/shares insight, first-2-sec watch, completion rate. Anything from trial reels or recent feature updates.]

🎯 ACCOUNT-SPECIFIC ANGLE
[For @{account} specifically, the ONE format+audio combo to test THIS week. Include hook opener.]

Rules:
- Be honest if you're unsure an audio is still hot — say so.
- Don't suggest anything that violates @{account}'s "do not" list.
- No generic "trending dance" fluff.
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=1000,
    )
