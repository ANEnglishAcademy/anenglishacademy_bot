# 🤖 AN English Academy Bot

Playful, bilingual Telegram bot (EN/RU) with on-demand dictionary `/translate`. Dockerized and CI-ready.

## Features
- Language choice EN 🇺🇸 / RU 🇷🇺
- `/translate <text>` — EN↔RU via LibreTranslate
- Clean UX, clear help, memory heartbeat logs
- Dockerfile + CI (GitHub Actions)

## Quick Start (Local)
1. Copy `.env.example` to `.env` and fill `BOT_TOKEN`.
2. Build & run:
   ```bash
   docker build -t anenglishacademy-bot .
   docker run --rm --env-file .env anenglishacademy-bot
