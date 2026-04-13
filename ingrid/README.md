# 📸 Ingrid — Content & Social Media Strategist

Ingrid is your sharp, data-minded content strategist for **@athena_hz** on Instagram. She handles content ideation, caption writing, hook testing, trend surfacing, content calendars, and post-performance analysis.

## Commands

**Create**
- `/idea [topic]` — Strategic content idea with hook, format, trial reel recommendation
- `/caption <topic>` — Draft caption in your voice
- `/caption_cn <topic>` — Bilingual caption (EN + CN)
- `/hooks <topic>` — 5 A/B hook variations for trial reel testing
- `/repurpose <content>` — Turn one post into a full week of content

**Strategy**
- `/trending` — What's trending on IG right now (audios, formats, algorithm)
- `/calendar` — Generate a 7-day content calendar
- `/review <description>` — Analyze how a post performed and what to do next

**Track**
- `/logpost <description>` — Log what you posted (feeds into calendar context)

**Chat**
- Text anything content-related and Ingrid replies

## Automated
- **Sunday 7 PM ET** — Weekly content recap + Monday priority

## Setup

1. Create a new Telegram bot via `@BotFather`, name it "Ingrid"
2. Get your chat ID (same as Moana's)
3. Add to `.env`:
   ```
   INGRID_TELEGRAM_BOT_TOKEN=your_token
   INGRID_TELEGRAM_CHAT_ID=your_chat_id
   ```
4. Run: `python -m ingrid`

## Future (Tier 3 — Instagram Graph API)
When connected, Ingrid will auto-pull analytics, track competitors, suggest optimal posting times, and generate data-driven weekly reports. Requires Meta developer app + Instagram Business account.
