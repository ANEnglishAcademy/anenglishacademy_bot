import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

from database.db import init_db
from handlers.onboarding import onboarding_router
from handlers.learning import learning_router
from handlers.menu import menu_router
from handlers.games import games_router
from handlers.skills import skills_router
from handlers.translate import translate_router
from handlers.profile import profile_router
from handlers.settings import settings_router
from handlers.help import help_router

# Load .env file for BOT_TOKEN
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_PATH = "/webhook"

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
dp.include_router(skills_router)
dp.include_router(translate_router)
dp.include_router(profile_router)
dp.include_router(settings_router)
dp.include_router(help_router)

async def on_startup(bot: Bot):
    logging.info("🤖 Initializing database...")
    await init_db()
    
    # Set the static "Menu" button with commands
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню / Main Menu"),
        BotCommand(command="help", description="Помощь / Help")
    ])
    
    if WEBHOOK_URL:
        logging.info(f"🔗 Setting webhook: {WEBHOOK_URL}{WEBHOOK_PATH}")
        await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")

async def on_shutdown(bot: Bot):
    logging.info("🛑 Container shutting down (scale to zero or update)...")
    if WEBHOOK_URL:
        logging.info("⚠️ Keeping webhook active on Telegram servers so Cloud Run can wake us up later!")
        # DO NOT call delete_webhook here!
    logging.info("Bot stopped!")

dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

def main():
    if WEBHOOK_URL:
        from aiohttp import web
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
        
        logging.info(f"🚀 Bot starting in WEBHOOK mode on port {PORT}")
        app = web.Application()

        # --- ВСТАВИТЬ СЮДА ---
        async def health_check(request):
            return web.Response(text="OK", status=200)

        app.router.add_get("/", health_check)
        app.router.add_get("/health", health_check)
        # ---------------------

        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        web.run_app(app, host="0.0.0.0", port=PORT)
    else:
        logging.info("🚀 Bot starting in POLLING mode")
        async def run_polling():
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
            
        asyncio.run(run_polling())

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
