# Athena Agents

A personal AI employee team, each running as an independent Telegram bot.

## The Team

| Agent | Role | Status |
|-------|------|--------|
| 🌊 **Moana** | Chief of Staff — morning brief, daily rhythm, general assistant | ✅ Active |
| 📸 **Ingrid** | Content & Social Media Strategist | 🔜 Planned |
| 💰 **Stella** | Finance & Investment Analyst | 🔜 Planned |
| 👑 **Manager** | Orchestrator — routes requests across all agents | 🔮 Future |

## Architecture

```
athena-agents/
├── core/                # Shared utilities (Telegram, Claude AI, config)
├── moana/               # Morning brief + daily rhythm agent
│   ├── services/        # Weather, news, calendar, deadlines
│   ├── formatters/      # Telegram message formatting
│   └── data/            # Deadlines, reminders (persistent)
├── ingrid/              # Content & social media (future)
├── stella/              # Finance & investment (future)
└── docker-compose.yml   # Run all agents
```

## Quick Start (Moana)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Fill in your API keys

# 3. Run
python -m moana
```

## Setup Guide

See [moana/README.md](moana/README.md) for detailed Telegram bot setup instructions.
