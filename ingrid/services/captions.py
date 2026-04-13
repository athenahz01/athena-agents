"""
Captions — draft Instagram captions in Athena's voice (bilingual option).
"""

import logging
from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def draft_caption(topic: str, bilingual: bool = False) -> str:
    """Draft an Instagram caption for @athena_hz."""
    lang_instruction = ""
    if bilingual:
        lang_instruction = (
            "Write the caption in BOTH English and Chinese (简体中文). "
            "Not a translation — write naturally in each language, "
            "like how a bilingual person would actually caption. "
            "English first, then Chinese below with a line break."
        )
    else:
        lang_instruction = (
            "Write in English. Casual, authentic tone — not influencer-fake. "
            "You can sprinkle in a Chinese phrase if it feels natural."
        )

    prompt = f"""Draft an Instagram caption for @athena_hz about: {topic}

{lang_instruction}

Requirements:
- Match Athena's voice: confident, slightly playful, real
- Include a strong opening line (this shows in the preview before "...more")
- Add a CTA at the end (question, save prompt, or share prompt)
- Suggest 15-20 relevant hashtags in a separate block at the end
- Keep the caption under 150 words (excluding hashtags)
- If relevant, suggest where to add line breaks for readability

Format:
[Caption text]

---
Hashtags:
[hashtag block]
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=600,
    )
