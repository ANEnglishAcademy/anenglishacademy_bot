import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, executor, types

# Logging
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TRANSLATE_URL = os.getenv("TRANSLATE_URL", "https://libretranslate.de/translate")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Health check
@dp.message_handler(commands=["health"])
async def health(message: types.Message):
    await message.reply("✅ Bot is running and healthy!")

# Start command
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🇬🇧 English", "🇷🇺 Russian")
    await message.answer(
        "👋 Welcome to AN English Academy Bot!\nPlease choose your language:",
        reply_markup=keyboard,
    )

# Language selection
@dp.message_handler(lambda m: m.text in ["🇬🇧 English", "🇷🇺 Russian"])
async def set_language(message: types.Message):
    lang = "en" if "English" in message.text else "ru"
    await message.answer(
        f"✅ Language set to {message.text}. Use /translate <word> to translate."
    )

# Translation command
@dp.message_handler(commands=["translate"])
async def translate_word(message: types.Message):
    args = message.get_args()
    if not args:
        await message.reply("❌ Please provide a word to translate. Example:\n/translate hello")
        return

    source_lang = "en"
    target_lang = "ru"
    if message.text.startswith("/translate "):
        text = args.strip()
    else:
        text = message.text.strip()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            TRANSLATE_URL,
            json={"q": text, "source": source_lang, "target": target_lang, "format": "text"},
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                await message.reply(f"🌍 Translation:\n{data.get('translatedText')}")
            else:
                await message.reply("⚠️ Translation service error.")

# Echo fallback
@dp.message_handler()
async def echo(message: types.Message):
    await message.reply("🤖 I didn’t understand that. Try /translate <word> or /start.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
