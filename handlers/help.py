from aiogram import types, Router

help_router = Router()

@help_router.message(commands=["help"])
async def send_help(message: types.Message):
    text = (
        "🤖 *Available Commands:*\n"
        "/start – Begin your journey\n"
        "/help – Show this help menu\n"
        "/personality – Choose bot personality\n"
        "/task – Get today’s task\n"
        "/profile – View your progress\n"
    )
    await message.answer(text, parse_mode="Markdown")
