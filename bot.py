import os
import logging
from aiogram import Bot, Dispatcher, executor, types

# Logging setup
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found. Please set it in Render Environment.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Startup
async def on_startup(dp):
    logging.info("🤖 SpeakEasy Bot started as @BlaBlaEnglishBot")

# Commands
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("👋 Welcome to SpeakEasy (@BlaBlaEnglishBot)!")

@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    await message.answer("ℹ️ Available commands:\n/start – Launch\n/help – Help\n/policy – Privacy Policy")

@dp.message_handler(commands=["policy"])
async def policy_cmd(message: types.Message):
    await message.answer("🔒 Privacy Policy: We do not store personal data. Conversations are for learning only.")

# Echo fallback
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
