"""
Shared Claude AI client used by all agents.
Each agent passes its own system prompt for personality.
"""

import logging
from collections import deque

import anthropic

log = logging.getLogger(__name__)

_client = None


def _get_client(api_key: str):
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def chat(
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
    history: deque | None = None,
    max_tokens: int = 1024,
) -> str:
    """Send a message with optional conversation history. Returns reply text."""
    client = _get_client(api_key)

    messages = list(history) if history else []
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )
        reply = response.content[0].text

        # Update history if provided
        if history is not None:
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        log.error(f"Claude API error: {e}")
        raise


def oneshot(
    api_key: str,
    model: str,
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 1024,
) -> str:
    """Single-turn request (no history). Used for translation, priorities, etc."""
    client = _get_client(api_key)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    except Exception as e:
        log.error(f"Claude oneshot error: {e}")
        raise
