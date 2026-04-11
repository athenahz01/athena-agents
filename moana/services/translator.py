"""
EN↔CN translation via Claude — auto-detects direction.
"""

import re
import logging
from core.claude_client import oneshot
from moana import config

log = logging.getLogger(__name__)

_TRANSLATOR_PROMPT = (
    "You are a bilingual EN↔CN translator. "
    "Keep translations natural and idiomatic, not robotic. "
    "For casual English, use casual Chinese (口语) and vice versa. "
    "Give both a natural/casual and a formal translation if they differ. "
    "Just give the translations, no explanation."
)


def translate(text: str) -> str:
    """Translate between English and Chinese. Auto-detects input language."""
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    is_chinese = chinese_chars > len(text) * 0.3

    if is_chinese:
        direction = "Chinese → English"
        prompt = f"Translate to English:\n\n{text}"
    else:
        direction = "English → 中文"
        prompt = f"Translate to Chinese (简体中文):\n\n{text}"

    result = oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=_TRANSLATOR_PROMPT,
    )
    return f"🔄 {direction}\n\n{result}"
