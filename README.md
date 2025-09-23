# SpeakEasy (@BlaBlaEnglishBot)

Fun English practice + quick EN⇄RU translation. Bilingual UI (EN/RU), on-demand `/translate`.

## Commands
- `/start` — start the bot
- `/help` — help
- `/lang` — switch interface EN/RU
- `/translate` <text> — translate; or reply `/translate` to any message
- `/settings` — view your settings
- `/about` — about the bot
- `/cancel` — cancel current action
- `/health` — health check (admin only)

## Deploy (Render, Docker)

1. Create a **Background Worker** (env: `docker`) from this repo.
2. In **Environment Variables**, set:
   - `BOT_TOKEN` — the token from BotFather
   - `ADMIN_ID` — your numeric Telegram user id (e.g., `1112146597`)
   - (optional) `TRANSLATE_URL` — default `https://libretranslate.com/translate`
   - (optional) `TRANSLATE_TIMEOUT` — default `8`
3. Deploy. Logs should show:
   - `Bot: SpeakEasy [@BlaBlaEnglishBot]`
   - `Start polling.`
   - `Updates were skipped successfully.` (expected once at start)

### Avoiding the “TerminatedByOtherGetUpdates” conflict
- Ensure **only one** instance of the bot is running:
  - Only one Render worker (Scaling = 1).
  - You’re **not** running the bot locally.
  - Webhooks are **not** set (we use long-polling). To confirm:
    - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo`
      - Must return `{"ok":true,"result":{"url":"" ...}}`
    - If any `url` is set, clear it:
      - `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook?drop_pending_updates=true`
- If you changed tokens or migrated services, redeploy once more to clear stale sessions.

## Config notes
- Python 3.11 (Dockerfile).
- `aiogram==2.25.1` + `aiohttp==3.8.6` (compatible).
- Polling worker (no public port, no webhooks).
- `/health` is admin-only (uses `ADMIN_ID`).

## Privacy
We do not store your messages or translations. Text is sent to the configured translation service (default: LibreTranslate) only to return a translation. See `PRIVACY.md`.

