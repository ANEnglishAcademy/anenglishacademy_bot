# ANEnglishAcademyBot (Docker, Render-ready)

Telegram study bot for bilingual (EN↔RU) on-demand translations with LibreTranslate.
Includes health check, auto-detected direction, and a quick "TR:" shortcut.

## What’s inside
- Python **3.11** (locked in Docker)
- aiogram **2.25.1**, aiohttp **3.8.6**
- Commands: `/start`, `/help`, `/ping`, `/translate`
- Quick translate: messages starting with `TR:`
- Minimal, stable worker (long-polling)

## Files
- `bot.py` — bot logic
- `requirements.txt` — pinned deps (compatible combo)
- `Dockerfile` — pins Python 3.11 and installs deps
- `.dockerignore` — clean Docker context
- `render.yaml` — Render worker config (env: docker)
- `.env.example` — local-development template
- `docker-compose.yml` — local run helper (optional)

## Environment Variables
Set these on Render (Service → Environment):
- `BOT_TOKEN` — BotFather token (required)
- `ADMIN_ID` — your numeric Telegram ID (optional, reserved)
- `TRANSLATE_URL` — e.g. `https://libretranslate.de/translate`
- `TRANSLATE_API_KEY` — (only if your LT instance needs a key)

## Deploy on Render (Background Worker)
1. Push this repo to GitHub.
2. On Render: **New → Background Worker → From Repo**.
   - Render will detect the `Dockerfile`.
3. Add Environment Variables (see above).
4. Deploy. Watch logs.

### Expected success logs
- pip finishes with `Successfully installed ...`
- Service starts without Python/aiohttp build errors
- Telegram polling begins (no crash)
- Sending `/ping` in Telegram replies with `✅ Bot is running`

## Local run (optional)
Create `.env` from `.env.example` and fill values.
```bash
docker-compose up --build
