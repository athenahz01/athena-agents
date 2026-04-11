"""
Telegram formatter — formats Moana's data into Telegram HTML messages.
"""

from moana import config


def format_full_brief(data: dict) -> list[str]:
    """Format the full morning brief. Returns list of messages."""
    messages = []
    hour = data.get("hour", 8)

    # ─── Header + Weather ────────────────────────────────────
    header = (
        f"🌊 <b>MOANA — Daily Brief</b>\n"
        f"📅 {data['date']}\n\n"
        f"{data['greeting']}"
    )

    if data.get("weather"):
        w = data["weather"]
        header += (
            f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
            f"☀️ <b>Ithaca Weather</b>\n"
            f"🌡️ {w['temp']}°F (feels like {w['feels_like']}°F)\n"
            f"📊 High {w['high']}°F / Low {w['low']}°F\n"
            f"💨 Wind {w['wind_speed']} mph · Humidity {w['humidity']}%\n"
            f"☁️ {w['description']}\n\n"
            f"👗 <b>Outfit:</b> {w['outfit_tip']}"
        )

    messages.append(header)

    # ─── Calendar ────────────────────────────────────────────
    cal_events = data.get("calendar", [])
    if cal_events:
        cal = "━━━━━━━━━━━━━━━━━━━━\n📅 <b>Today's Schedule</b>\n\n"
        for event in cal_events:
            time_str = event["start_time"]
            if event.get("end_time"):
                time_str += f" → {event['end_time']}"
            loc = f"\n   📍 {event['location']}" if event.get("location") else ""
            cal += f"⏰ <b>{time_str}</b>\n   {event['summary']}{loc}\n\n"
        messages.append(cal.strip())
    else:
        messages.append("━━━━━━━━━━━━━━━━━━━━\n📅 <b>Today's Schedule</b>\n\nNothing on the calendar today — open day!")

    # ─── News ────────────────────────────────────────────────
    news_data = data.get("news", {})
    if news_data:
        summary = news_data.get("summary") if isinstance(news_data, dict) else None
        raw = news_data.get("raw", news_data) if isinstance(news_data, dict) else news_data

        if summary:
            # Claude-written conversational brief
            news_text = (
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📰 <b>Today's Brief</b>\n\n"
                f"{summary}"
            )
            messages.append(news_text.strip())
        elif raw:
            # Fallback: raw headlines
            news_text = "━━━━━━━━━━━━━━━━━━━━\n📰 <b>Your News Feed</b>\n"
            for key, articles in raw.items():
                if not articles:
                    continue
                label = config.NEWS_CATEGORIES.get(key, {}).get("label", key)
                news_text += f"\n<b>{label}</b>\n"
                for i, a in enumerate(articles[:4], 1):
                    title = _esc(str(a.get("title", "Untitled")))
                    url = a.get("url", "")
                    raw_source = a.get("source", "")
                    source = _esc(str(raw_source)) if isinstance(raw_source, str) else ""
                    if url:
                        line = f'{i}. <a href="{url}">{title}</a>'
                    else:
                        line = f"{i}. {title}"
                    if source:
                        line += f"  <i>({source})</i>"
                    news_text += line + "\n"
            messages.append(news_text.strip())

    # ─── Deadlines ───────────────────────────────────────────
    dl_data = data.get("deadlines", {})
    deadlines = dl_data.get("deadlines", [])
    reminders = dl_data.get("reminders", [])

    if deadlines or reminders:
        dl = "━━━━━━━━━━━━━━━━━━━━\n📌 <b>Deadlines & Reminders</b>\n\n"
        for d in deadlines[:5]:
            days = d["days_left"]
            icon = "🔴" if days <= 2 else "🟡" if days <= 5 else "🟢"
            dl += f"{icon} <b>{d['title']}</b> — {days} days left\n"
        if reminders:
            dl += "\n💭 <b>Reminders:</b>\n"
            for r in reminders[:5]:
                rtxt = r["text"] if isinstance(r, dict) else str(r)
                dl += f"  • {rtxt}\n"
        messages.append(dl.strip())

    # ─── Quote + sign-off (time-aware) ───────────────────────
    quote = data.get("quote", "")

    if hour < 12:
        signoff = "Have a great day!"
    elif hour < 17:
        signoff = "Strong rest of the day!"
    elif hour < 21:
        signoff = "Finish the day strong!"
    else:
        signoff = "Get some rest tonight!"

    messages.append(
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ {quote}\n\n"
        f"{signoff}\n"
        f"— Moana 🌊"
    )

    return messages


def format_weather_quick(weather: dict) -> str:
    w = weather
    return (
        f"☀️ <b>Ithaca Weather</b>\n\n"
        f"🌡️ {w['temp']}°F (feels like {w['feels_like']}°F)\n"
        f"📊 High {w['high']}°F / Low {w['low']}°F\n"
        f"💨 Wind {w['wind_speed']} mph · Humidity {w['humidity']}%\n"
        f"☁️ {w['description']}\n\n"
        f"👗 {w['outfit_tip']}"
    )


def format_news_section(news_data: dict) -> str:
    """Format for standalone /news command."""
    if isinstance(news_data, dict) and news_data.get("summary"):
        return f"📰 <b>Latest Brief</b>\n\n{news_data['summary']}"

    # Fallback to raw
    raw = news_data.get("raw", news_data) if isinstance(news_data, dict) else news_data
    text = "📰 <b>Latest Headlines</b>\n"
    for key, articles in raw.items():
        if not articles:
            continue
        label = config.NEWS_CATEGORIES.get(key, {}).get("label", key)
        text += f"\n<b>{label}</b>\n"
        for i, a in enumerate(articles[:3], 1):
            title = _esc(str(a.get("title", "Untitled")))
            url = a.get("url", "")
            if url:
                text += f'{i}. <a href="{url}">{title}</a>\n'
            else:
                text += f"{i}. {title}\n"
    return text.strip()


def format_deadlines(dl_data: dict) -> str:
    deadlines = dl_data.get("deadlines", [])
    reminders = dl_data.get("reminders", [])

    if not deadlines and not reminders:
        return "📌 No upcoming deadlines or reminders! Clear schedule 🎉"

    text = "📌 <b>Upcoming Deadlines</b>\n\n"
    for d in deadlines:
        days = d["days_left"]
        icon = "🔴" if days <= 2 else "🟡" if days <= 5 else "🟢"
        text += f"{icon} <b>{d['title']}</b>\n   Due in {days} days ({d['date'][:10]})\n\n"
    if reminders:
        text += "💭 <b>Reminders</b>\n"
        for i, r in enumerate(reminders, 1):
            rtxt = r["text"] if isinstance(r, dict) else str(r)
            text += f"{i}. {rtxt}\n"
    return text.strip()


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_weekly_recap(data: dict) -> str:
    """Format the Sunday weekly recap message."""
    lines = [
        f"🌊 <b>Moana — Weekly Recap</b>",
        f"📅 Week of {data['week_start']} – {data['week_end']}",
        "",
    ]

    # Completions
    completed = data.get("completed_count", 0)
    completed_items = data.get("completed_items", [])
    missed = data.get("missed", [])

    lines.append("━━━━━━━━━━━━━━━━━━━━")

    if completed > 0 or missed:
        lines.append("📌 <b>Deadlines & Tasks</b>")
        if completed > 0:
            lines.append(f"  ✅ {completed} completed this week")
            for item in completed_items[:5]:
                lines.append(f"      • {item}")
        if missed:
            lines.append(f"  🔴 {len(missed)} overdue")
            for m in missed[:5]:
                lines.append(f"      • {m.get('title', 'Untitled')}")
        lines.append("")

    # Active reminders
    reminders = data.get("active_reminders", [])
    if reminders:
        lines.append(f"💭 <b>{len(reminders)} active reminder(s)</b>")
        for r in reminders[:5]:
            rtxt = r["text"] if isinstance(r, dict) else str(r)
            lines.append(f"  • {rtxt}")
        lines.append("")

    # Check-in stats
    checkins = data.get("checkins", 0)
    active_days = data.get("active_days", 0)
    most_active = data.get("most_active_day")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("📊 <b>Activity</b>")
    lines.append(f"  💬 {checkins} check-ins across {active_days} days")
    if most_active:
        lines.append(f"  🔥 Most active: {most_active}")
    lines.append("")

    # Next week preview
    next_week = data.get("next_week_deadlines", [])
    if next_week:
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("👀 <b>Coming up next week</b>")
        for d in next_week[:5]:
            lines.append(f"  📋 {d['title']} — {d['days_left']} days left")
        lines.append("")

    # Sign-off
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("Reset, recharge, come back stronger.")
    lines.append("See you Monday morning! 🌊")

    return "\n".join(lines)