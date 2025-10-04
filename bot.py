import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

# Load .env file for BOT_TOKEN
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in environment!")

# Logging
logging.basicConfig(level=logging.INFO)

# Create bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# -------------------- COMMAND HANDLERS --------------------

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Welcome to AN English Academy!\nType /help to see what I can do.")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "📚 Available commands:\n"
        "/start – Greet the user\n"
        "/help – Show this menu\n"
        "/setlevel – Choose your English level"
    )

@dp.message(Command("setlevel"))
async def set_level(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="A1"), types.KeyboardButton(text="A2")],
            [types.KeyboardButton(text="B1"), types.KeyboardButton(text="B2")],
            [types.KeyboardButton(text="C1")]
        ],
        resize_keyboard=True
    )
    await message.answer("📊 Choose your English level:", reply_markup=keyboard)

# -------------------- START BOT --------------------

async def main():
    logging.info("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
