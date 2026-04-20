"""
Review — analyze post performance against the playbook's KPI priority.
"""

import logging
from core.claude_client import oneshot
from ingrid import config

log = logging.getLogger(__name__)


def review_post(description: str, account: str = None) -> str:
    """Analyze performance with playbook KPI priority (saves > shares > watch time > comments > profile > follows > likes)."""
    account = account or config.DEFAULT_ACCOUNT
    acct = config.account_config(account)

    prompt = f"""Athena is describing her latest post on @{account}: {description}

Account positioning: {acct.get('positioning', '')}

PLAYBOOK KPI PRIORITY (in order of what actually matters):
1. Saves — signals content worth returning to (highest algorithmic weight 2026)
2. Shares — signals worth sending to someone
3. Watch time / completion rate — first 2 seconds decide distribution
4. Comments — engaged audience > passive
5. Profile visits — interest in YOU
6. Follows from a post — conversion metric that matters
7. Likes — vanity, barely matters for distribution

PLAYBOOK RED FLAGS (apply if patterns show):
- Views declining WoW → format too varied, not consistent enough
- Followers up, engagement down → audience misaligned, bold reveal attracting wrong crowd
- Saves < 1% of views → not save-worthy, need more specificity/reflection
- Follows stalling under 1k for 6+ weeks → positioning not hitting, rework hooks

Give Athena:

📊 PERFORMANCE ASSESSMENT
[Is this good/avg/underperforming for @{account}? Which KPI matters MOST for this content type and how did it do on that KPI?]

🔍 WHY IT PERFORMED THIS WAY
[2-3 specific reasons — hook strength (did it match playbook hook rules?), format choice, timing, pillar fit, audio fit. Be direct.]

🚩 RED FLAG CHECK
[Any of the playbook red flags triggered? If yes, which one and the fix.]

🔄 WHAT TO DO NEXT
[Repurpose? Double down? Pivot? Specific next-post adjustments.]

🧪 TEST SUGGESTION
[ONE trial reel idea using what you learned. Playbook-compliant hook + format.]

Be direct and data-minded. No cheerleading. No "great job!"
"""

    return oneshot(
        api_key=config.ANTHROPIC_API_KEY,
        model=config.CLAUDE_MODEL,
        prompt=prompt,
        system_prompt=config.SYSTEM_PROMPT,
        max_tokens=900,
    )
