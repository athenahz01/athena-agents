"""
Countdown helper — the backbone of Athena's @athena_huo arc.

Given today's date, reports:
- Days until graduation (May 23, 2026)
- Current act (act 1 / bridge / act 2)
- Current phase within act 1 (establish / open loop / land moment)
- Countdown caption suffix ("X to go." / "today." / bridge / new countdown)
"""

from datetime import date, datetime
from pathlib import Path
import json

STRATEGY_FILE = Path(__file__).parent.parent / "data" / "strategy.json"

GRADUATION = date(2026, 5, 23)
ACT_1_START = date(2026, 4, 23)
BRIDGE_END = date(2026, 5, 31)
MOVING_WEEK_END = date(2026, 6, 6)


def _load_strategy() -> dict:
    if STRATEGY_FILE.exists():
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_context(today: date | None = None) -> dict:
    """Return full countdown/arc context for today."""
    today = today or datetime.now().date()
    days_to_grad = (GRADUATION - today).days

    # Act + phase detection
    if today < ACT_1_START:
        act = "pre-launch"
        phase = "Pre-launch"
        phase_focus = "Account not live yet."
    elif ACT_1_START <= today <= GRADUATION:
        act = "act_1"
        if today <= date(2026, 5, 2):
            phase = "Phase 1: Establish the World"
            phase_focus = "Introduce character (you), place (Ithaca), premise. Aesthetic daily life + last-times."
        elif today <= date(2026, 5, 12):
            phase = "Phase 2: Open the Loop"
            phase_focus = "Countdown becomes explicit. Graduation prep starts. 1-2 posts hit above baseline."
        else:
            phase = "Phase 3: Land the Moment"
            phase_focus = "Daily posting. Outfit reveals, cap-and-gown, senior week. Graduation reel is hero."
    elif GRADUATION < today <= BRIDGE_END:
        act = "bridge"
        phase = "Bridge: packing + final Ithaca"
        phase_focus = "Pre-shot packing footage, apartment in boxes, last Ithaca moments."
    elif BRIDGE_END < today <= MOVING_WEEK_END:
        act = "moving_week"
        phase = "Moving Week"
        phase_focus = "Apartment arrival, first NYC days."
    else:
        act = "act_2"
        phase = "Act 2: NYC era"
        phase_focus = "Figuring it out + first job + NYC aesthetic + the moat."

    # Countdown suffix for captions
    if today == GRADUATION:
        countdown_suffix = "today."
    elif ACT_1_START <= today < GRADUATION:
        countdown_suffix = f"{days_to_grad} to go."
    elif GRADUATION < today <= BRIDGE_END:
        countdown_suffix = None  # bridge \u2014 no countdown
    elif BRIDGE_END < today <= MOVING_WEEK_END:
        countdown_suffix = None  # moving week
    elif today > MOVING_WEEK_END:
        # New NYC countdown \u2014 weeks since arrival
        days_in_nyc = (today - date(2026, 6, 7)).days
        weeks_in_nyc = days_in_nyc // 7 + 1
        countdown_suffix = f"week {weeks_in_nyc} in nyc."
    else:
        countdown_suffix = None

    return {
        "today": today.isoformat(),
        "days_to_graduation": days_to_grad,
        "act": act,
        "phase": phase,
        "phase_focus": phase_focus,
        "countdown_suffix": countdown_suffix,
    }


def get_context_summary() -> str:
    """Human-readable summary for Telegram display."""
    ctx = get_context()
    lines = [f"\ud83d\udcc6 <b>Arc Context</b>"]
    lines.append(f"Today: {ctx['today']}")
    if ctx["days_to_graduation"] > 0:
        lines.append(f"\ud83c\udf93 <b>{ctx['days_to_graduation']} days to graduation</b>")
    elif ctx["days_to_graduation"] == 0:
        lines.append("\ud83c\udf93 <b>Graduation day.</b>")
    else:
        lines.append(f"\ud83c\udf93 {abs(ctx['days_to_graduation'])} days since graduation")
    lines.append(f"Act: {ctx['act']}")
    lines.append(f"Phase: {ctx['phase']}")
    lines.append(f"<i>{ctx['phase_focus']}</i>")
    if ctx["countdown_suffix"]:
        lines.append(f"\nCaption suffix: <b>{ctx['countdown_suffix']}</b>")
    return "\n".join(lines)


def current_pillars() -> list:
    """Return the content pillars for the current act."""
    strategy = _load_strategy()
    ctx = get_context()
    pillars_block = strategy.get("content_pillars", {})

    if ctx["act"] in ("pre-launch", "act_1"):
        return pillars_block.get("act_1", {}).get("pillars", [])
    elif ctx["act"] in ("bridge", "moving_week"):
        # Transition \u2014 show both for planning
        return pillars_block.get("act_1", {}).get("pillars", []) + pillars_block.get(
            "act_2", {}
        ).get("pillars", [])
    else:
        return pillars_block.get("act_2", {}).get("pillars", [])
