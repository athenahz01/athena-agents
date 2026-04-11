# 🌊 Moana — Chief of Staff

Moana is your daily rhythm manager. She sends a personalized morning brief every day and stays available on Telegram for weather, news, deadlines, translation, and general chat.

## What She Does

**Morning Brief (auto-sent daily at 8 AM ET)**
- ☀️ Ithaca weather + outfit suggestion
- 📅 Today's Google Calendar events
- 📰 Curated news: U.S., World, AI/Tech, Startups
- 📌 Upcoming deadlines & reminders
- ✨ Bilingual motivational quote

**Commands**
- `/brief` — Full morning brief on demand
- `/weather` — Quick Ithaca weather
- `/news` — Latest headlines
- `/deadlines` — Upcoming deadlines
- `/remind <text>` — Set a quick reminder
- `/cn <text>` — Translate EN↔CN
- `/priorities` — AI-generated top 3 for today
- Free text — Chat with Moana via Claude AI

**What She Doesn't Do (other agents' jobs)**
- Content/Instagram → Ingrid 📸
- Finance/Stocks → Stella 💰

## Setup

### 1. Create Telegram Bot
1. Open Telegram → search `@BotFather`
2. `/newbot` → name it "Moana"
3. Copy the bot token

### 2. Get Your Chat ID
1. Message your bot
2. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Find `chat.id`

### 3. API Keys
- **Telegram Bot Token** — BotFather
- **OpenWeather** — free at openweathermap.org
- **GNews** — free at gnews.io
- **Anthropic** — for Claude AI chat
- **Google Calendar** — OAuth credentials (optional)

### 4. Run
```bash
cd athena-agents
cp .env.example .env  # fill in keys
pip install -r requirements.txt
python -m moana
```
