import os
import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# ---------- Config ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")  # set in Render/ENV
TRANSLATE_API_URL = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.de/translate")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "EN")  # EN or RU
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ---------- Logging ----------
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ANEnglishAcademyBot")

# ---------- Bot ----------
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it to environment variables.")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

# In-memory user prefs (replace with DB later if needed)
# { user_id: {"lang":"EN"|"RU"} }
USER_PREFS = {}

# ---------- Helpers ----------
def get_user_lang(user_id: int) -> str:
    return USER_PREFS.get(user_id, {}).get("lang", DEFAULT_LANGUAGE)

def set_user_lang(user_id: int, lang: str):
    USER_PREFS[user_id] = USER_PREFS.get(user_id, {})
    USER_PREFS[user_id]["lang"] = "EN" if lang.upper().startswith("EN") else "RU"

def is_ascii(s: str) -> bool:
    try:
        s.encode("ascii")
        return True
    except Exception:
        return False

def translate_word(q: str, target_lang: str) -> str:
    """
    target_lang: 'en' or 'ru'
    Auto-detect source: if ASCII → source=en else source=ru
    """
    source_lang = "en" if is_ascii(q) else "ru"
    if target_lang not in ("en", "ru"):
        target_lang = "ru" if source_lang == "en" else "en"

    payload = {
        "q": q,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }
    try:
        r = requests.post(TRANSLATE_API_URL, data=payload, timeout=12)
        r.raise_for_status()
        data = r.json()
        return data.get("translatedText") or "⚠️ Translation not available."
    except Exception as e:
        logger.exception("Translate error: %s", e)
        return "⚠️ Translation service failed. Try again later."

async def send_lang_menu(message: types.Message, intro_text: str):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(types.KeyboardButton("English 🇺🇸"),
           types.KeyboardButton("Русский 🇷🇺"))
    await message.answer(intro_text, reply_markup=kb)

# ---------- Commands ----------
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    set_user_lang(message.from_user.id, DEFAULT_LANGUAGE)
    await send_lang_menu(
        message,
        "👋 Welcome to <b>AN English Academy</b> bot!\n"
        "Choose your interface language / Выбери язык интерфейса:"
    )

@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    text_en = (
        "🤖 <b>Commands</b>\n"
        "/start — choose interface language\n"
        "/help — this help\n"
        "/mode — switch EN/RU interface\n"
        "/translate <word or phrase> — on-demand EN↔RU\n\n"
        "Examples:\n"
        "• /translate hello\n"
        "• /translate спасибо\n"
    )
    text_ru = (
        "🤖 <b>Команды</b>\n"
        "/start — выбрать язык интерфейса\n"
        "/help — помощь\n"
        "/mode — переключить EN/RU\n"
        "/translate <слово или фраза> — перевод EN↔RU по запросу\n\n"
        "Примеры:\n"
        "• /translate hello\n"
        "• /translate спасибо\n"
    )
    await message.answer(text_en if lang == "EN" else text_ru)

@dp.message_handler(commands=["mode"])
async def cmd_mode(message: types.Message):
    await send_lang_menu(
        message,
        "🔁 Switch interface language / Переключить язык интерфейса:"
    )

@dp.message_handler(commands=["about"])
async def cmd_about(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    text_en = "🌸 <b>AN English Academy</b>: playful, smart, bilingual. Let’s Level Up your English!"
    text_ru = "🌸 <b>AN English Academy</b>: легко, умно и двуязычно. Прокачаем твой английский!"
    await message.answer(text_en if lang == "EN" else text_ru)

@dp.message_handler(commands=["translate"])
async def cmd_translate(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        lang = get_user_lang(message.from_user.id)
        if lang == "EN":
            return await message.reply("❌ Please provide text to translate. Example: <code>/translate hello</code>")
        return await message.reply("❌ Введите текст для перевода. Пример: <code>/translate спасибо</code>")
    query = parts[1].strip()
    # Decide direction based on input script by default
    target = "ru" if is_ascii(query) else "en"
    result = translate_word(query, target)
    arrow = "→"
    flag = "🇷🇺" if target == "ru" else "🇺🇸"
    await message.reply(f"🔄 <b>Translate</b> {arrow} {flag}\n\n<i>{query}</i>\n<b>{result}</b>")

# ---------- Language buttons ----------
@dp.message_handler(lambda m: m.text in ["English 🇺🇸", "Русский 🇷🇺"])
async def handle_lang_pick(message: types.Message):
    if "English" in message.text:
        set_user_lang(message.from_user.id, "EN")
        await message.answer("✅ Interface set to English. Type /help to see commands.",
                             reply_markup=types.ReplyKeyboardRemove())
    else:
        set_user_lang(message.from_user.id, "RU")
        await message.answer("✅ Язык интерфейса: Русский. Наберите /help для списка команд.",
                             reply_markup=types.ReplyKeyboardRemove())

# ---------- Health / Memory log (debug-friendly) ----------
async def memory_heartbeat():
    try:
        import psutil
        proc = psutil.Process()
        while True:
            mem = proc.memory_info().rss / 1024**2
            logger.info("Memory usage: %.2f MB", mem)
            await asyncio.sleep(180)
    except Exception as e:
        logger.warning("Heartbeat disabled: %s", e)

# ---------- Run ----------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(memory_heartbeat())
    executor.start_polling(dp, skip_updates=True)
# Stable Python for aiogram/aiohttp
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (faster wheels & stable requests)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
TRANSLATE_API_URL = os.getenv("TRANSLATE_API_URL")
TRANSLATE_API_KEY = os.getenv("TRANSLATE_API_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
