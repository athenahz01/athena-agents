"""
Shared Telegram utilities used by all agents.
"""

import logging
from telegram.ext import Application
from telegram.constants import ParseMode

log = logging.getLogger(__name__)


async def send_message(
    app: Application,
    chat_id: str,
    text: str,
    parse_mode=ParseMode.HTML,
):
    """Send a message, auto-splitting if too long for Telegram's 4096 char limit."""
    MAX_LEN = 4000

    chunks = []
    while len(text) > MAX_LEN:
        split_at = text.rfind("\n", 0, MAX_LEN)
        if split_at == -1:
            split_at = MAX_LEN
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    chunks.append(text)

    for chunk in chunks:
        if chunk.strip():
            try:
                await app.bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    parse_mode=parse_mode,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                log.warning(f"HTML send failed, retrying plain: {e}")
                await app.bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    disable_web_page_preview=True,
                )
