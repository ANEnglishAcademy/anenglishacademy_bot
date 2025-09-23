BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in environment!")
print(f"Loaded token: {BOT_TOKEN[:10]}...")  # print first 10 chars for safety
bot = Bot(token=BOT_TOKEN)
