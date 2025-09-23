import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in environment variables!")

print(f"✅ Loaded BOT_TOKEN (first 6 chars): {BOT_TOKEN[:6]}...")
