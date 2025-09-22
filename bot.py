import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import aiohttp

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# LibreTranslate endpoint
TRANSLATE_URL = "https://libretranslate.de/translate"

# Start command
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer(
        "👋 Welcome to AN English Academy Bot!\n"
        "Choose your options:\n"
        "• Use /translate <word or phrase> to translate EN ↔ RU\n"
        "• More features coming soon 🎸"
    )

# Translate command
@dp.message_handler(commands=["translate"])
async def translate_command(message: types.Message):
    args = message.get_args()
    if not args:
        await message.answer("❗Please provide text to translate.\nExample: /translate hello")
        return

    source_lang = "en" if all(ord(c) < 128 for c in args) else "ru"
    target_lang = "ru" if source_lang == "en" else "en"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            TRANSLATE_URL,
            json={"q": args, "source": source_lang, "target": target_lang, "format": "text"}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                translated = result.get("translatedText", "⚠️ Translation failed")
                await message.answer(f"🔄 {translated}")
            else:
                await message.answer("⚠️ Translation service error. Try again later.")

# Health check
@dp.message_handler(commands=["health"])
async def health_command(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("✅ Bot is running healthy!")
    else:
        await message.answer("🚫 You don’t have permission to check health.")

# Fallback handler
@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("❓ I didn’t understand that. Try /translate <text>.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
