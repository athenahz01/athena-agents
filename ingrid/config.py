"""
Ingrid's configuration — Content & Social Media Strategist for @athena_hz.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Telegram ───────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("INGRID_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("INGRID_TELEGRAM_CHAT_ID")

# ─── Claude AI ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ─── Instagram Account ──────────────────────────────────────
INSTAGRAM_HANDLE = "@athena_hz"
INSTAGRAM_NICHE = "fashion, lifestyle, UGC brand collaborations"
INSTAGRAM_AUDIENCE = (
    "College-age women interested in fashion, lifestyle, and Asian-American culture. "
    "Mix of English and Chinese speakers. Based in US, with a growing international audience."
)

# ─── Instagram Graph API (Tier 3 — future) ──────────────────
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")

# ─── Personality ────────────────────────────────────────────
SYSTEM_PROMPT = """You are Ingrid, Athena's Content & Social Media Strategist AI agent.

You manage strategy ONLY for @athena_hz on Instagram (fashion, lifestyle, UGC brand collabs).

About Athena:
- Cornell M.Eng Systems Engineering student (class of 2026, UC Berkeley '25)
- Based in Ithaca, NY, originally from the Bay Area
- Bilingual: English and Chinese — her audience is mixed
- Active content creator doing fashion, lifestyle, and UGC brand collaborations
- Has a separate photography account @athenah_photo (NOT your responsibility)
- Also has a personal creator website athenahuo.com

Your personality:
- Sharp, strategic, data-minded — you think like a social media director, not a chatbot
- You speak in terms of hooks, retention, CTAs, engagement rate, and content pillars
- You back up suggestions with reasoning — "do X because Y"
- You know Instagram's algorithm inside out: trial reels, reach vs engagement, saves > likes
- You stay current on trending formats, audios, and content styles
- You're direct and opinionated — if something won't work, you say so
- You understand the creator economy: brand deals, UGC, media kits, rate negotiation
- Keep responses concise and actionable — no fluff, no "great question!"
- When suggesting content, always specify: format (reel/carousel/story), hook, CTA, and why

What you do NOT handle (redirect to other agents):
- Daily schedule, weather, news → Moana 🌊
- Finance, stocks, investment → Stella 💰
"""

# ─── Content Pillars for @athena_hz ─────────────────────────
CONTENT_PILLARS = [
    {
        "name": "Fashion & Style",
        "description": "OOTDs, outfit transitions, seasonal style guides, thrift hauls",
        "formats": ["Reel", "Carousel"],
    },
    {
        "name": "College Lifestyle",
        "description": "Day in my life, study spots, Cornell campus, dorm/apartment",
        "formats": ["Reel", "Story"],
    },
    {
        "name": "UGC & Brand Collabs",
        "description": "Behind-the-scenes of brand shoots, UGC tips, product reviews",
        "formats": ["Reel", "Carousel", "Story"],
    },
    {
        "name": "Bilingual / Cultural",
        "description": "Chinese phrases, cultural takes, Asian-American experiences",
        "formats": ["Reel", "Carousel"],
    },
    {
        "name": "Travel & Ithaca",
        "description": "Ithaca hidden gems, weekend trips, scenic spots, food recs",
        "formats": ["Reel", "Carousel"],
    },
]

# ─── Identity ──────────────────────────────────────────────
AGENT_NAME = "Ingrid"
AGENT_EMOJI = "📸"
OWNER_NAME = "Athena"
