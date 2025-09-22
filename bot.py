import logging
import os
import requests
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")  
ADMIN_ID = int(os.getenv("1112146597"))
TRANSLATE_URL = os.getenv("TRANSLATE_URL")
TRANSLATE_LANG = os.getenv("TRANSLATE_LANG", "ru")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Start command
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer(
        "👋 Welcome to AN English Academy Bot!\n\n"
        "Type /help to see available commands."
    )

# Help command
@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await message.answer(
        "🤖 Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this message\n"
        "/translate <word> - Translate a word into Russian"
    )

# Translate command
@dp.message_handler(commands=["translate"])
async def translate_word(message: types.Message):
    args = message.get_args()
    if not args:
        await message.answer("⚠️ Please provide a word to translate.")
        return

    try:
        response = requests.post(
            TRANSLATE_URL,
            data={"q": args, "source": "en", "target": TRANSLATE_LANG, "format": "text"},
        )
        if response.status_code == 200:
            translated = response.json()["translatedText"]
            await message.answer(f"🔤 {args} → {translated}")
        else:
            await message.answer("❌ Error with translation service.")
    except Exception as e:
        await message.answer(f"⚠️ Translation failed: {e}")

# Health check
@dp.message_handler(commands=["health"])
async def health_command(message: types.Message):
    await message.answer("✅ Bot is running fine!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
