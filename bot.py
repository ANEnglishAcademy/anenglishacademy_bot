import logging
import os
import re
import requests
from aiogram import Bot, Dispatcher, executor, types

# ========= Config =========
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # reserved for possible admin-only features
TRANSLATE_URL = os.getenv("TRANSLATE_URL", "https://libretranslate.de/translate")
TRANSLATE_API_KEY = os.getenv("TRANSLATE_API_KEY")  # only if your instance needs it

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

# ========= Logging =========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ANEnglishAcademyBot")

# ========= Bot =========
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Simple Cyrillic detector for EN↔RU auto-detect
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")

def detect_lang_pair(text: str):
    # If it contains Cyrillic → assume RU→EN, else EN→RU
    if CYRILLIC_RE.search(text):
        return ("ru", "en")
    return ("en", "ru")

def translate_text(text: str) -> str:
    src, tgt = detect_lang_pair(text)
    payload = {
        "q": text,
        "source": src,
        "target": tgt,
        "format": "text"
    }
    if TRANSLATE_API_KEY:
        payload["api_key"] = TRANSLATE_API_KEY

    r = requests.post(TRANSLATE_URL, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    # LibreTranslate returns {"translatedText": "..."}
    return data.get("translatedText") or data.get("result") or ""

# ========= Commands =========
@dp.message_handler(commands=["start"])
async def cmd_start(m: types.Message):
    await m.reply(
        "👋 Welcome to <b>ANEnglishAcademyBot</b>!\n\n"
        "Use <code>/translate your text</code> for instant EN↔RU translation (auto-detect).\n"
        "Try: <code>/translate hello</code> or <code>/translate привет</code>\n\n"
        "Health check: <code>/ping</code>\n"
        "Help: <code>/help</code>"
    )

@dp.message_handler(commands=["help"])
async def cmd_help(m: types.Message):
    await m.reply(
        "📚 <b>Commands</b>\n"
        "• /start — welcome & instructions\n"
        "• /help — this menu\n"
        "• /ping — health check\n"
        "• /translate <text> — EN↔RU translation (auto-detect)\n\n"
        "Shortcuts:\n"
        "• Send messages starting with <code>TR:</code> to translate quickly.\n"
        "  Example: <code>TR: good morning</code>"
    )

@dp.message_handler(commands=["ping"])
async def cmd_ping(m: types.Message):
    await m.reply("✅ Bot is running")

@dp.message_handler(commands=["translate"])
async def cmd_translate(m: types.Message):
    text = m.get_args().strip()
    if not text:
        await m.reply("✍️ Usage: <code>/translate your text</code>\nExample: <code>/translate hello</code>")
        return
    try:
        translated = translate_text(text)
        if not translated:
            await m.reply("❌ Translation returned empty result.")
            return
        await m.reply(f"🔤 <b>Original:</b> {text}\n🗣 <b>Translated:</b> {translated}")
    except requests.HTTPError as e:
        logger.exception("HTTP error during translation")
        code = getattr(e.response, "status_code", "unknown")
        await m.reply(f"❌ Translation HTTP error: {code}")
    except Exception:
        logger.exception("Translation error")
        await m.reply("❌ Translation error. Please try again.")

# Quick inline translate: messages starting with "TR:"
@dp.message_handler(lambda m: m.text and m.text.strip().lower().startswith("tr:"))
async def quick_tr(m: types.Message):
    text = m.text.split(":", 1)[1].strip()
    if not text:
        await m.reply("Send: <code>TR: your text</code>")
        return
    try:
        translated = translate_text(text)
        await m.reply(f"🗣 {translated}")
    except Exception:
        logger.exception("Quick translate failed")
        await m.reply("❌ Quick translate error.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
