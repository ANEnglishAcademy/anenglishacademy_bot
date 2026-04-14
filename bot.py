import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from database.db import init_db
from handlers.onboarding import onboarding_router
from handlers.learning import learning_router
from handlers.menu import menu_router
from handlers.games import games_router
from handlers.translate import translate_router
from handlers.profile import profile_router
from handlers.settings import settings_router
from handlers.help import help_router

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

# Include Routers
dp.include_router(onboarding_router)
dp.include_router(learning_router)
dp.include_router(menu_router)
dp.include_router(games_router)
dp.include_router(translate_router)
dp.include_router(profile_router)
dp.include_router(settings_router)
dp.include_router(help_router)

async def main():
    logging.info("🤖 Initializing database...")
    await init_db()
    
    logging.info("🚀 Bot is starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
