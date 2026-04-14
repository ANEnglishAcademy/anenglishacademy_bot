import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import get_user, get_top_users, reset_progress
from utils.helpers import get_badge, get_progress_bar, get_streak_message

profile_router = Router()

@profile_router.message(Command("profile"))
@profile_router.message(F.text.in_({"👤 Profile", "👤 Профиль"}))
@profile_router.callback_query(F.data == "menu_profile")
async def cmd_profile(event: types.Message | types.CallbackQuery):
    if isinstance(event, types.CallbackQuery):
        message = event.message
        user_id = event.from_user.id
        await event.answer()
    else:
        message = event
        user_id = message.from_user.id
    
    user = await get_user(user_id)
    
    if not user:
        await message.answer("Please /start first!")
        return

    nickname = user.get("nickname", "Student")
    level = user.get("level", "A1")
    personality = user.get("personality", "hippie")
    tasks_completed = user.get("tasks_completed", 0)
    streak = user.get("streak_days", 0)
    best_streak = user.get("best_streak", 0)
    joined_at = user.get("joined_at", "").split("T")[0]
    referrals = user.get("referrals_count", 0)
    
    badge_emoji, badge_name = get_badge(tasks_completed)
    progress_bar = get_progress_bar(tasks_completed)
    
    # Bilingual check
    lang_mode = user.get("language_mode", "english")
    is_bilingual = (lang_mode == "bilingual")
    
    if is_bilingual:
        teacher_label = "Учитель"
        level_label = "Уровень"
        joined_label = "Присоединился"
        rank_label = "Ранг"
        tasks_label = "Задания"
        streak_label = "Серия"
        best_streak_label = "Рекорд"
        invites_label = "Приглашено друзей"
        settings_btn_text = "⚙️ Настройки"
        invite_btn_text = "🎁 Пригласить друга"
        days_text = "дней"
        title_text = f"👤 *Профиль: {nickname}*"
    else:
        teacher_label = "Teacher"
        level_label = "Level"
        joined_label = "Joined"
        rank_label = "Rank"
        tasks_label = "Tasks Done"
        streak_label = "Current Streak"
        best_streak_label = "Best Streak"
        invites_label = "Invited Friends"
        settings_btn_text = "⚙️ Settings"
        invite_btn_text = "🎁 Invite a Friend"
        days_text = "days"
        title_text = f"👤 *Profile: {nickname}*"

    text = (
        f"{title_text}\n\n"
        f"📚 {level_label}: *{level}*\n"
        f"🤖 {teacher_label}: *{personality.capitalize()}*\n"
        f"📅 {joined_label}: {joined_at}\n\n"
        f"🏆 {rank_label}: {badge_emoji} *{badge_name}*\n"
        f"{progress_bar}\n\n"
        f"✅ {tasks_label}: *{tasks_completed}*\n"
        f"🔥 {streak_label}: *{streak}* {days_text}\n"
        f"🏅 {best_streak_label}: *{best_streak}* {days_text}\n"
        f"👥 {invites_label}: *{referrals}*\n"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text=invite_btn_text, callback_data="invite_friend")
    builder.button(text=settings_btn_text, callback_data="settings_main")
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@profile_router.callback_query(F.data == "invite_friend")
async def process_invite_friend(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user and user.get("language_mode") == "bilingual")
    
    bot_info = await callback.bot.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start=ref{user_id}"
    
    if is_bilingual:
        text = (
            "🎁 *Твоя пригласительная ссылка!*\n\n"
            f"`{invite_link}`\n\n"
            "Отправь её друзьям, чтобы помочь им начать изучать английский! 🚀"
        )
    else:
        text = (
            "🎁 *Your invite link!*\n\n"
            f"`{invite_link}`\n\n"
            "Send this to your friends to start learning English together! 🚀"
        )
        
    await callback.message.reply(text, parse_mode="Markdown")
    await callback.answer()

@profile_router.message(Command("top"))
async def cmd_top(message: types.Message):
    top_users = await get_top_users(limit=10)
    
    if not top_users:
        await message.answer("No students yet! Be the first! 🥇")
        return
        
    text = "🏆 *Leaderboard — Top Students*\n\n"
    for i, u in enumerate(top_users, 1):
        name = u.get("nickname", f"User {u['user_id']}")
        tasks = u.get("tasks_completed", 0)
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} *{name}* — {tasks} tasks\n"
        
    await message.answer(text, parse_mode="Markdown")

@profile_router.message(Command("resetprogress"))
async def cmd_reset_ask(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Yes, reset!", callback_data="reset_confirm")
    builder.button(text="❌ No, cancel", callback_data="reset_cancel")
    builder.adjust(2)
    
    await message.answer(
        "⚠️ *Wait! Are you sure?*\n\n"
        "This will delete your streak, badges, and progress.\n"
        "Your nickname and settings will be saved.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@profile_router.callback_query(F.data == "reset_confirm")
async def process_reset_confirm(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await reset_progress(user_id)
    await callback.message.edit_text("🔄 Progress aligned to zero. New game! Use /task to start fresh.", parse_mode="Markdown")

@profile_router.callback_query(F.data == "reset_cancel")
async def process_reset_cancel(callback: types.CallbackQuery):
    await callback.message.edit_text("👍 Phew! Your progress is safe.", parse_mode="Markdown")
