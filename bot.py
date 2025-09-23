import os
import re
import json
import logging
from typing import Tuple

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import aiohttp

logging.basicConfig(level=logging.INFO)

# ========= Simple in-memory user prefs (per-process) =========
user_lang = {}  # user_id -> "en" | "ru"

# ========= Utils =========
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")

def pick_direction(text: str) -> Tuple[str, str]:
    """Decide EN->RU or RU->EN based on presence of Cyrillic."""
    if CYRILLIC_RE.search(text):
        return "ru", "en"
    return "en", "ru"

async def lt_translate(session: aiohttp.ClientSession, text: str) -> str:
    """Translate via LibreTranslate (no API key assumed)."""
    text = (text or "").strip()
    if not text:
        return "Nothing to translate."
    source, target = pick_direction(text)
    payload = {"q": text, "source": source, "target": target, "format": "text"}
    try:
        async with session.post(TRANSLATE_URL, data=payload, timeout=TRANSLATE_TIMEOUT) as resp:
            if resp.status != 200:
                body = await resp.text()
                return f"⚠️ Translation error ({resp.status}): {body[:300]}"
            data = await resp.json()
            if isinstance(data, dict) and "translatedText" in data:
                return data["translatedText"]
            return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        return f"⚠️ Translation failed: {e}"

def t(uid: int, en: str, ru: str) -> str:
    """Bilingual UI helper."""
    return ru if user_lang.get(uid, "en") == "ru" else en

# ========= Command registration =========
async def set_bot_commands() -> None:
    en_cmds = [
        types.BotCommand("start", "Start SpeakEasy"),
        types.BotCommand("help", "How to use the bot"),
        types.BotCommand("lang", "Switch interface language (EN/RU)"),
        types.BotCommand("translate", "Translate a word or phrase (EN⇄RU)"),
        types.BotCommand("settings", "View your settings"),
        types.BotCommand("about", "About the bot"),
        types.BotCommand("cancel", "Cancel current action"),
        types.BotCommand("health", "Health check (admin)"),
    ]
    ru_cmds = [
        types.BotCommand("start", "Запуск бота"),
        types.BotCommand("help", "Как пользоваться ботом"),
        types.BotCommand("lang", "Сменить язык интерфейса (EN/RU)"),
        types.BotCommand("translate", "Перевести слово или фразу (EN⇄RU)"),
        types.BotCommand("settings", "Посмотреть настройки"),
        types.BotCommand("about", "О боте"),
        types.BotCommand("cancel", "Отменить текущее действие"),
        types.BotCommand("health", "Проверка бота (для админа)"),
    ]
    # Default list (no language code) = EN
    await bot.set_my_commands(en_cmds, scope=types.BotCommandScopeDefault())
    # RU localization
    await bot.set_my_commands(ru_cmds, scope=types.BotCommandScopeDefault(), language_code="ru")

# ========= Handlers =========
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    # Initialize interface language from Telegram settings
    user_lang[uid] = "ru" if (message.from_user.language_code or "").startswith("ru") else "en"
    greeting = t(
        uid,
        "👋 Welcome to <b>SpeakEasy</b> (@BlaBlaEnglishBot)! I help you learn English in a fun, practical way.\n\n"
        "• Use <code>/lang</code> to switch my interface (EN/RU)\n"
        "• Use <code>/translate</code> + text or reply to a message to translate (EN⇄RU)\n"
        "• See all commands: <code>/help</code>",
        "👋 Привет! Это <b>SpeakEasy</b> (@BlaBlaEnglishBot). Помогаю учить английский легко и с кайфом.\n\n"
        "• Сменить язык интерфейса: <code>/lang</code>\n"
        "• Перевод: <code>/translate</code> + текст или ответом на сообщение (EN⇄RU)\n"
        "• Все команды: <code>/help</code>",
    )
    await message.reply(greeting)

@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    uid = message.from_user.id
    text = t(
        uid,
        "🧭 <b>Help</b>\n"
        "• <code>/start</code> — start the bot\n"
        "• <code>/help</code> — show this help\n"
        "• <code>/lang</code> — switch interface language (EN/RU)\n"
        "• <code>/translate</code> <i>text</i> — translate a word/phrase (EN⇄RU), or reply to a message with /translate\n"
        "• <code>/settings</code> — view current settings\n"
        "• <code>/about</code> — about the bot\n"
        "• <code>/cancel</code> — cancel current action\n"
        "• <code>/health</code> — health check (admin only)",
        "🧭 <b>Помощь</b>\n"
        "• <code>/start</code> — запустить бота\n"
        "• <code>/help</code> — показать помощь\n"
        "• <code>/lang</code> — сменить язык интерфейса (EN/RU)\n"
        "• <code>/translate</code> <i>текст</i> — перевод слова/фразы (EN⇄RU), либо ответьте /translate на нужное сообщение\n"
        "• <code>/settings</code> — текущие настройки\n"
        "• <code>/about</code> — о боте\n"
        "• <code>/cancel</code> — отмена текущего действия\n"
        "• <code>/health</code> — проверка бота (только админ)",
    )
    await message.reply(text)

@dp.message_handler(commands=["lang"])
async def cmd_lang(message: types.Message):
    uid = message.from_user.id
    cur = user_lang.get(uid, "en")
    user_lang[uid] = "ru" if cur == "en" else "en"
    txt = t(uid, "Language set to English 🇺🇸", "Язык интерфейса: русский 🇷🇺")
    await message.reply(txt)

@dp.message_handler(commands=["settings"])
async def cmd_settings(message: types.Message):
    uid = message.from_user.id
    lang_name = "English 🇺🇸" if user_lang.get(uid, "en") == "en" else "Русский 🇷🇺"
    txt = t(
        uid,
        f"⚙️ <b>Settings</b>\n• Interface: {lang_name}\n• Translate: on-demand via /translate",
        f"⚙️ <b>Настройки</b>\n• Интерфейс: {lang_name}\n• Перевод: по запросу через /translate",
    )
    await message.reply(txt)

@dp.message_handler(commands=["about"])
async def cmd_about(message: types.Message):
    uid = message.from_user.id
    txt = t(
        uid,
        "📚 <b>SpeakEasy (@BlaBlaEnglishBot)</b>\nFun English practice + quick EN⇄RU translation.\nPrivacy: type /help to learn more.",
        "📚 <b>SpeakEasy (@BlaBlaEnglishBot)</b>\nВесёлый английский + быстрый перевод EN⇄RU.\nПро приватность см. /help.",
    )
    await message.reply(txt)

@dp.message_handler(commands=["cancel"])
async def cmd_cancel(message: types.Message):
    uid = message.from_user.id
    txt = t(uid, "✅ Nothing to cancel. You’re all set.", "✅ Отменять нечего. Всё ок.")
    await message.reply(txt)

@dp.message_handler(commands=["health"])
async def cmd_health(message: types.Message):
    uid = message.from_user.id
    if uid != ADMIN_ID:
        await message.reply("🚫 Admins only.")
        return
    try:
        me = await bot.get_me()
        await message.reply(
            f"✅ Bot OK\n"
            f"• name: {me.first_name}\n"
            f"• username: @{me.username}\n"
            f"• polling: active"
        )
    except Exception as e:
        await message.reply(f"⚠️ Health error: {e}")

@dp.message_handler(commands=["translate"])
async def cmd_translate(message: types.Message):
    uid = message.from_user.id
    # Use replied text first; else arguments after /translate
    src_text = None
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        src_text = (message.reply_to_message.text or message.reply_to_message.caption).strip()
    else:
        src_text = message.get_args().strip() if message.get_args() else ""

    if not src_text:
        prompt = t(uid, "Reply to a message or type: /translate your text",
                        "Ответьте на сообщение или напишите: /translate ваш текст")
        await message.reply(prompt)
        return

    async with aiohttp.ClientSession() as session:
        translated = await lt_translate(session, src_text)
    await message.reply(f"<b>→</b> {translated}")

@dp.message_handler(lambda m: m.text and m.text.lower().startswith("translate "))
async def freeform_translate(message: types.Message):
    text = message.text[9:].strip()
    if not text:
        return
    async with aiohttp.ClientSession() as session:
        translated = await lt_translate(session, text)
    await message.reply(f"<b>→</b> {translated}")

# ========= Startup =========
async def on_startup(dispatcher: Dispatcher):
    await set_bot_commands()
    logging.info("Bot commands set.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
