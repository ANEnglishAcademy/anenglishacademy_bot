import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import Throttled

# Logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- Health Check ---
@dp.message_handler(commands=['health'])
async def health(message: types.Message):
    await message.answer("✅ Bot is alive and running!")

# --- Dictionary Lookup ---
@dp.message_handler(commands=['translate'])
async def translate(message: types.Message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 2:
            await message.reply("Usage: /translate <word>")
            return
        word = parts[1]

        # Dummy bilingual dictionary (EN <-> RU)
        dictionary = {
            "hello": "привет",
            "dog": "собака",
            "cat": "кот",
            "love": "любовь",
            "peace": "мир",
            "teacher": "учитель",
            "student": "студент"
        }

        if word.lower() in dictionary:
            result = dictionary[word.lower()]
            await message.answer(f"🔤 {word} → {result}")
        elif word.lower() in [v.lower() for v in dictionary.values()]:
            # Reverse lookup (RU → EN)
            for eng, ru in dictionary.items():
                if ru.lower() == word.lower():
                    await message.answer(f"🔤 {word} → {eng}")
                    return
        else:
            await message.answer("❌ Word not found in dictionary.")
    except Exception as e:
        logging.error(f"Error in translate: {e}")
        await message.reply("⚠️ Something went wrong. Try again.")

# --- Admin Ping ---
@dp.message_handler(commands=['ping'])
async def ping(message: types.Message):
    if str(message.from_user.id) == ADMIN_ID:
        await message.answer("🏓 Pong! Bot is responsive.")
    else:
        await message.answer("⛔ You are not authorized to use this command.")

# --- Start Command ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("👋 Hello! I’m your English Academy Bot.\n\n"
                         "Available commands:\n"
                         "• /health → check bot status\n"
                         "• /translate <word> → lookup EN/RU word\n"
                         "• /ping → admin only\n")

# --- Run ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
