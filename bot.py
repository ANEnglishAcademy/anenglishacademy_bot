import logging
import os
from aiogram import Bot, Dispatcher, executor, types

# Logging
logging.basicConfig(level=logging.INFO)

# Load variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Init bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Health check command
@dp.message_handler(commands=["health"])
async def health_check(message: types.Message):
    await message.reply("✅ Bot is running fine!")

# Start command
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.reply("👋 Welcome to AN English Academy Bot! Type /help to see options.")

# Help command
@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    await message.reply("Commands:\n/start - start\n/help - this menu\n/health - check bot status")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
