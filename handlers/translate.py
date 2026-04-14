import logging
import os
import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from utils.helpers import translate_word

translate_router = Router()

TRANSLATE_API_URL = os.getenv("TRANSLATE_API_URL", "https://libretranslate.de/translate")
TRANSLATE_LANG = os.getenv("TRANSLATE_LANG", "ru")

async def get_translation(text: str, target_lang: str = TRANSLATE_LANG) -> str | None:
    """Fetch translation from API."""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "q": text,
                "source": "en",
                "target": target_lang,
                "format": "text"
            }
            async with session.post(TRANSLATE_API_URL, json=payload, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("translatedText")
                else:
                    logging.error(f"Translation API error: {resp.status}")
    except Exception as e:
        logging.error(f"Translation exception: {e}")
    return None

@translate_router.message(Command("translate"))
async def cmd_translate(message: types.Message):
    # Parse: /translate word
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.answer("⚠️ Usage: `/translate word`", parse_mode="Markdown")
        return

    word = parts[1].strip()
    
    # 1. Check local dictionary
    local_translation = translate_word(word)
    if local_translation:
        await message.answer(f"📖 *{word}* — {local_translation}", parse_mode="Markdown")
        return

    # 2. API Fallback
    await message.answer("🔍 Searching dictionary...")
    
    translation = await get_translation(word)
    
    if translation:
        await message.answer(f"🌐 *{word}* — {translation}", parse_mode="Markdown")
    else:
        await message.answer("❌ Could not translate this phrase.")
