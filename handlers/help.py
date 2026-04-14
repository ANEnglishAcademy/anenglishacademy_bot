from aiogram import types, Router, F
from aiogram.filters import Command

help_router = Router()

@help_router.message(Command("help"))
@help_router.message(F.text.in_({"🆘 Help", "🆘 Помощь"}))
@help_router.callback_query(F.data == "menu_help")
async def send_help(event: types.Message | types.CallbackQuery):
    if isinstance(event, types.CallbackQuery):
        message = event.message
        user_id = event.from_user.id
        await event.answer()
    else:
        message = event
        user_id = message.from_user.id
        
    from database.db import get_user
    user = await get_user(user_id)
    is_bilingual = (user and user.get("language_mode") == "bilingual")

    if is_bilingual:
        text = (
            "🤖 *Доступные команды:*\n\n"
            "🌱 *Начало*\n"
            "/start – Начать обучение\n"
            "/help – Показать это меню\n\n"
            "📚 *Учеба*\n"
            "/task – Получить задание\n"
            "Просто пишите ответ! (без команд)\n"
            "/grammar – Грамматическая подсказка\n"
            "/translate <слово> – Перевод слова\n\n"
            "⚙️ *Настройки*\n"
            "/settings – Главное меню настроек\n"
            "   (Уровень, Учитель, Язык)\n\n"
            "👤 *Профиль*\n"
            "/profile – Ваша статистика\n"
            "/top – Рейтинг учеников\n"
            "/resetprogress – Сброс прогресса"
        )
    else:
        text = (
            "🤖 *Available Commands:*\n\n"
            "🌱 *Start*\n"
            "/start – Begin your journey\n"
            "/help – Show this menu\n\n"
            "📚 *Learning*\n"
            "/task – Get today’s task\n"
            "Just type your answer! (No command needed)\n"
            "/grammar – Show grammar tip\n"
            "/translate <word> – Translate word\n\n"
            "⚙️ *Settings*\n"
            "/settings – Main Settings Menu\n"
            "   (Change Level, Teacher, Language)\n\n"
            "👤 *Profile*\n"
            "/profile – View your stats\n"
            "/top – Leaderboard\n"
            "/resetprogress – Reset all progress"
        )
    
    await message.answer(text, parse_mode="Markdown")
