"""
Hooks — generate hook variations following the playbook's strict hook rules.
"""

import logging
from core.claude_client import oneshot
from ingrid import config
from ingrid.services.countdown import get_context

log = logging.getLogger(__name__)


def generate_hooks(topic: str, count: int = 5, account: str = None) -> str:
    """Generate playbook-compliant hook variations for a Reel."""
    account = account or config.DEFAULT_ACCOUNT
    acct = config.account_config(account)
    ctx = get_context()

    # For @athena_huo, enforce the strict 3-hook-type rule
    if account == "athena_huo":
        hook_constraint = """STRICT HOOK RULES (@athena_huo playbook):
Every hook MUST do ONE of these three things:
  A) Drop a specific number (e.g., "I woke up at 9:48. 28 days before graduation.")
  B) Contradict a belief (e.g., "The last month at Cornell is not what it looks like on Instagram.")
  C) State something uncomfortable (e.g., "I cried in the library last night.")

NEVER open with: "people keep asking me," "everyone says," "so today," "guys," "hi guys," "New post!"

For each of the {count} hooks:
1. The exact opening line (first 2 seconds, spoken or shown)
2. Which type: A / B / C
3. Visual description (face to camera? specific b-roll reveal?)
4. Predicted strength (🔥🔥🔥 / 🔥🔥 / 🔥)

End with: pick the TOP 2 to test as trial reels and say why.
Each of the 5 hooks must be genuinely different — don't just reword."""
    else:
        hook_constraint = """@athena_hz is the polished portfolio account. Hooks should be editorial, fashion-led, visual-first.

For each of the {count} hooks:
1. The visual or statement shown/said in the first 2 seconds
2. Hook type (outfit reveal / product showcase / editorial statement / transformation)
3. Visual description
4. Predicted strength (🔥🔥🔥 / 🔥🔥 / 🔥)"""

    countdown_note = ""
    if account == "athena_huo" and ctx["countdown_suffix"] and ctx["act"] == "act_1":
        countdown_note = f"\nCURRENT COUNTDOWN CONTEXT: Today is {ctx['days_to_graduation']} days before graduation. You can reference the number in numerical hooks if natural."

    prompt = f"""Generate {count} hook variations for an Instagram Reel about: {topic}

Target account: @{account}
Positioning: {acct.get('positioning', '')}
Voice: {acct.get('voice', acct.get('tone', ''))}
{countdown_note}

{hook_constraint.format(count=count)}
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=900,
    )
