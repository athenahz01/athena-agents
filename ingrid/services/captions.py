"""
Captions — draft captions following the strict playbook rules per account.
"""

import logging
from core.claude_client import oneshot
from ingrid import config
from ingrid.services.countdown import get_context

log = logging.getLogger(__name__)


def draft_caption(topic: str, bilingual: bool = False, account: str = None) -> str:
    """Draft a caption following the playbook for the target account."""
    account = account or config.DEFAULT_ACCOUNT
    acct = config.account_config(account)
    ctx = get_context()

    # @athena_huo has a strict DITL caption structure
    if account == "athena_huo":
        # Build day number
        day_num = ""
        if ctx["act"] == "act_1" and ctx["days_to_graduation"] is not None:
            # Day N of the arc — launch was apr 23 (day 1)
            from datetime import date
            launch = date(2026, 4, 23)
            today = date.fromisoformat(ctx["today"])
            n = (today - launch).days + 1
            if n >= 1:
                day_num = f"day {n}"

        structure = f"""REQUIRED DITL CAPTION STRUCTURE:
"{day_num}. [one specific observation about the day]. {ctx.get('countdown_suffix') or ''}"

Examples from the playbook:
- "day one. the ordinary ones go the fastest. 29 to go."
- "day two. slow is a skill. 28 to go."
- "day three. collecting the small things. 27 to go."

OR if this is a BOLD REVEAL post (rare — 1/wk max):
2-4 reflective sentences. No lists. No emojis. No CTA. Just one coherent thought delivered like prose.

CAPTION RULES (absolute):
- Documenting, not explaining. Never teach or instruct.
- Max 2 emojis. Prefer zero.
- Never start with "New post!", "Hi guys", "So today"
- Never use the word "girlies"
- NO hashtags in caption — those go in the first comment

Produce:
1. THE CAPTION (exact text, playbook-compliant)
2. FIRST COMMENT hashtag mix (exactly 5 tags: 2 niche + 2 mid + 1 broad from the playbook tags)"""

        lang_instruction = ""
        if bilingual:
            lang_instruction = "\n\nAfter the English caption, add a short Chinese line (中文) that feels natural — not a translation, just one observation in Chinese. Keep the countdown/day in English."

    else:
        # @athena_hz — editorial fashion caption
        structure = """@athena_hz is polished editorial fashion portfolio.

Requirements:
- Opening line that reads well in the preview before "...more"
- Editorial voice — brand-deal-ready. Not overly casual, not corporate.
- 1 CTA allowed at end if it feels natural (save / share / question)
- Under 120 words
- Suggest 10-15 hashtags in a separate block

Produce:
1. THE CAPTION (editorial, fashion-first)
2. HASHTAG BLOCK (separate, at the end)"""
        lang_instruction = ""
        if bilingual:
            lang_instruction = "\n\nInclude both English and Chinese (中文) — not a literal translation, written naturally in each."

    prompt = f"""Draft a caption for @{account} about: {topic}

Account positioning: {acct.get('positioning', '')}
Voice: {acct.get('voice', acct.get('tone', ''))}
{lang_instruction}

{structure}
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=700,
    )
