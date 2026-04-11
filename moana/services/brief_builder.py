"""
Brief builder — gathers all of Moana's data sources into one dict.
"""

import logging
import random
from datetime import datetime

import pytz
from moana import config

log = logging.getLogger(__name__)

_QUOTES = [
    "You're not behind. You're building something most people don't have the guts to start.",
    "She remembered who she was and the game changed.",
    "Not lucky — just prepared, consistent, and a little obsessed.",
    "Plot twist: you were the main character this whole time.",
    "Protect your energy. Not everyone deserves access to you.",
    "The version of you that's scared is not the version that's running the show today.",
    "Bet on yourself. The odds are better than you think.",
    "You don't need a sign. You ARE the sign. Go.",
    "Everything you want is on the other side of 'I don't feel like it.'",
    "Soft life, hard work. Both at the same time.",
    "This is your era. Act like it.",
    "You're one decision away from a completely different life.",
    "She built it quietly, then let the results make the noise.",
    "Your future self is watching. Make her proud.",
    "Closed mouths don't get fed. Ask for what you want.",
    "Romanticize your life — even the boring parts.",
    "Reminder: you've survived 100% of your worst days so far.",
    "Main character energy isn't given. It's chosen.",
    "The universe is rearranging things in your favor. Let it.",
    "Trust the girl who got you this far. She knows what she's doing.",
]


def build_morning_brief() -> dict:
    """Collect all data for the morning brief."""
    from moana.services.weather import get_weather
    from moana.services.news import get_all_news
    from moana.services.calendar_service import get_todays_events
    from moana.services.deadlines import get_upcoming_deadlines

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)

    data = {
        "date": now.strftime("%A, %B %d, %Y"),
        "day_of_week": now.strftime("%A"),
        "hour": now.hour,
        "greeting": None,
        "weather": None,
        "calendar": [],
        "news": {},
        "deadlines": {"deadlines": [], "reminders": []},
        "quote": random.choice(_QUOTES),
    }

    # Weather
    try:
        data["weather"] = get_weather()
        log.info(f"Weather: {data['weather']['temp']}°F")
    except Exception as e:
        log.error(f"Weather failed: {e}")

    # Calendar
    try:
        data["calendar"] = get_todays_events()
        log.info(f"Calendar: {len(data['calendar'])} events")
    except Exception as e:
        log.info(f"Calendar skipped: {e}")

    # News
    try:
        data["news"] = get_all_news()
        for key, articles in data["news"].items():
            log.info(f"  {key}: {len(articles)} articles")
    except Exception as e:
        log.error(f"News failed: {e}")

    # Deadlines — 21 day window so nothing sneaks up
    try:
        data["deadlines"] = get_upcoming_deadlines(days_ahead=21)
    except Exception as e:
        log.error(f"Deadlines failed: {e}")

    # Build greeting AFTER we have weather + calendar for context
    data["greeting"] = _get_greeting(
        now.hour,
        now.strftime("%A"),
        data.get("weather"),
        data.get("calendar", []),
    )

    return data


def _get_greeting(
    hour: int, day: str, weather: dict | None, calendar: list
) -> str:
    """Contextual greeting that references weather/schedule when relevant."""

    if hour < 6:
        opener = "Up before the sun? Respect"
    elif hour < 10:
        opener = "Good morning Athena"
    elif hour < 12:
        opener = "Late morning catch-up"
    elif hour < 17:
        opener = "Afternoon check-in"
    elif hour < 21:
        opener = "Evening recap"
    else:
        opener = "Night owl edition"

    extras = []

    if weather:
        temp = weather["temp"]
        desc = weather["description"].lower()
        if "rain" in desc or "drizzle" in desc:
            extras.append("rainy day ahead")
        elif "snow" in desc:
            extras.append("snow day!")
        elif temp >= 75:
            extras.append("it's a warm one")
        elif temp <= 32:
            extras.append("it's freezing out there")

    if calendar:
        n = len(calendar)
        if n == 1:
            extras.append("1 thing on the calendar")
        elif n > 1:
            extras.append(f"{n} things on the calendar")

    if day == "Friday":
        extras.append("happy Friday")
    elif day == "Monday":
        extras.append("new week, let's go")

    if extras:
        return f"{opener} — {', '.join(extras)}."
    return f"{opener}."