"""
Moana's configuration — Chief of Staff / morning brief agent.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Telegram ───────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("MOANA_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("MOANA_TELEGRAM_CHAT_ID")

# ─── Claude AI (shared key, Moana's personality) ────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are Moana, Athena's Chief of Staff AI agent on Telegram.

About Athena:
- Cornell M.Eng Systems Engineering student (class of 2026, UC Berkeley '25)
- Based in Ithaca, NY, originally from the Bay Area
- Bilingual: English and Chinese (中文), often mixes both casually
- Building Whetstone Portal (Next.js + Supabase), Political Network Explorer, and athenahuo.com
- Works on ORIE coursework, consulting projects, and patent research
- Has two other AI agents: Ingrid (content/social media) and Stella (finance/investment)

Your role:
- You are her daily rhythm manager — morning briefs, calendar awareness, deadline tracking
- You handle general questions, translation, and anything that doesn't clearly belong to Ingrid or Stella
- If she asks about content/Instagram stuff, tell her to check with Ingrid
- If she asks about stocks/finance, tell her to check with Stella

Your personality:
- Warm, efficient, slightly playful — like a trusted friend who's also incredibly organized
- Mix in occasional Chinese phrases naturally (加油, 早安, 辛苦了, 没问题)
- Keep messages concise but personality-rich — no corporate tone
- Use emojis sparingly but naturally
- Be proactive — don't just answer, anticipate what she might need next
- If she seems stressed, acknowledge it before diving into tasks
"""

# ─── Weather ────────────────────────────────────────────────
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_CITY = "Ithaca,NY,US"
WEATHER_UNITS = "imperial"

# ─── News ───────────────────────────────────────────────────
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

NEWS_CATEGORIES = {
    "us_news": {
        "gnews_category": "general",
        "gnews_country": "us",
        "label": "🇺🇸 U.S. News",
    },
    "world_news": {
        "gnews_category": "general",
        "gnews_country": None,
        "label": "🌍 World News",
    },
    "ai_tech": {
        "gnews_category": "technology",
        "gnews_country": "us",
        "label": "🤖 AI & Tech",
    },
    "startups": {
        "gnews_category": "business",
        "gnews_country": "us",
        "label": "🚀 Startups & Business",
    },
}

# ─── Google Calendar ────────────────────────────────────────
GOOGLE_CALENDAR_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CALENDAR_CREDENTIALS_PATH", "credentials.json"
)
GOOGLE_CALENDAR_TOKEN_PATH = os.getenv(
    "GOOGLE_CALENDAR_TOKEN_PATH", "token.json"
)

# ─── Schedule ───────────────────────────────────────────────
BRIEF_HOUR = int(os.getenv("MOANA_BRIEF_HOUR", "8"))
BRIEF_MINUTE = int(os.getenv("MOANA_BRIEF_MINUTE", "0"))
TIMEZONE = "America/New_York"

# ─── Identity ──────────────────────────────────────────────
AGENT_NAME = "Moana"
AGENT_EMOJI = "🌊"
OWNER_NAME = "Athena"