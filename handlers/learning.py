import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.db import get_user, increment_progress, update_user
from data.curriculum import CURRICULUM
from data.personalities import get_reaction, get_greeting
from utils.helpers import evaluate_answer, get_streak_message, get_badge, get_next_badge_info, get_progress_bar

learning_router = Router()

async def get_task_data(user):
    level = user["level"] or "A1"
    week = user["current_week"]
    day = user["current_day"]
    
    # Handle curriculum completion (loop back or stay at end?)
    # DB logic loops back to week 1 if > 4.
    
    week_data = CURRICULUM.get(level, {}).get(week, {})
    day_data = week_data.get(day, {})
    
    return day_data, level, week, day

@learning_router.message(Command("task"))
@learning_router.message(F.text.in_({"📚 Task", "📚 Задание"}))
@learning_router.callback_query(F.data.in_({"next_task", "menu_task"}))
async def cmd_task(event: types.Message | types.CallbackQuery):
    if isinstance(event, types.CallbackQuery):
        message = event.message
        user_id = event.from_user.id
        await event.answer() # Acknowledge callback
    else:
        message = event
        user_id = message.from_user.id
    user = await get_user(user_id)
    
    if not user or not user["onboarding_complete"]:
        await message.answer("Please finish onboarding first using /start!")
        return

    task_data, level, week, day = await get_task_data(user)
    
    if not task_data:
        await message.answer("No task found! Please contact support or /resetprogress.")
        return

    # Bilingual check
    lang_mode = user.get("language_mode", "english")
    is_bilingual = (lang_mode == "bilingual" and level in ["A1", "A2", "B1"])
    
    if is_bilingual:
        topic = task_data.get('topic_ru') or task_data.get('topic')
        task_text = task_data.get('task_ru') or task_data.get('task')
        
        text = (
            f"📅 *Неделя {week}, День {day}*  |  Уровень: {level}\n"
            f"Тема: *{topic}*\n\n"
            f"{task_text}\n\n"
            "👉 *Напишите ваш ответ ниже!* 👇" 
        )
    else:
        topic = task_data.get('topic')
        task_text = task_data.get('task')
        
        text = (
            f"📅 *Week {week}, Day {day}*  |  Level: {level}\n"
            f"Topic: *{topic}*\n\n"
            f"{task_text}\n\n"
            "👉 *Type your answer below!* 👇" 
        )
    
    # Add "I don't understand" button if no RU translation or if English mode
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    # Check if we already have static translation
    has_ru = bool(task_data.get('topic_ru') and task_data.get('task_ru'))
    
    # Show button if:
    # 1. Not bilingual (so user might need help)
    # 2. Bilingual but static translation missing (B2/C1)
    if not is_bilingual or (is_bilingual and not has_ru):
        btn_text = "❓ I don't understand" if not is_bilingual else "❓ Перевод"
        builder.button(text=btn_text, callback_data=f"translate_task_{level}_{week}_{day}")
    
    builder.adjust(1)
    
    if isinstance(event, types.Message):
         await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
         # For callback (Next Task), maybe edit the message or send new one? 
         # Best to send new one so history is kept? 
         # Standard behavior for "Next task" is usually a new message.
         await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@learning_router.callback_query(F.data.startswith("translate_task_"))
async def btn_translate_task(callback: types.CallbackQuery):
    # Parse callback: translate_task_LEVEL_WEEK_DAY
    try:
        _, _, level, week, day = callback.data.split("_")
        week = int(week)
        day = int(day)
    except ValueError:
        await callback.answer("Error parsing task data.")
        return

    # Fetch task data
    week_data = CURRICULUM.get(level, {}).get(week, {})
    task_data = week_data.get(day, {})
    
    if not task_data:
        await callback.answer("Task not found.")
        return
        
    topic = task_data.get('topic')
    task_text = task_data.get('task')
    
    # Check for static first
    topic_ru = task_data.get('topic_ru')
    task_ru = task_data.get('task_ru')
    
    from handlers.translate import get_translation
    
    # Translate if missing
    if not topic_ru:
        await callback.answer("Translating topic...", show_alert=False)
        topic_ru = await get_translation(topic) or "Translation unavailable"
        
    if not task_ru:
        await callback.answer("Translating task...", show_alert=False)
        task_ru = await get_translation(task_text) or "Translation unavailable"
        
    text = (
        f"🇷🇺 *Перевод:*\n\n"
        f"Тема: {topic_ru}\n"
        f"Задание: {task_ru}"
    )
    
    await callback.message.reply(text, parse_mode="Markdown")
    await callback.answer()

@learning_router.message(F.text, ~F.text.startswith("/"))
async def check_answer(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        return
        
    user_id = message.from_user.id
    user_text = message.text.strip()
    
    # Ignore menu buttons
    if user_text in ["📚 Task", "👤 Profile", "⚙️ Settings", "🆘 Help"]:
        return

    user = await get_user(user_id)
    if not user:
        return

    # Check if user has an active task session? 
    # For now, we assume if they type something non-command, it's an answer attempt
    # BUT only if they have onboarding done.
    if not user.get("onboarding_complete"):
        return

    task_data, level, week, day = await get_task_data(user)
    
    if not task_data:
        # No task data found? Maybe they finished everything or DB error.
        # Silently ignore or suggest /task? 
        # Better to safeguard: if asking for task, they use /task or button.
        # If random chat, we might reply "I'm waiting for your answer to: <Topic>"
        return
    
    keywords = task_data.get("keywords", [])
    result = evaluate_answer(user_text, keywords)
    personality_key = user["personality"] or "hippie"
    
    if result == "correct" or result == "funny":
        # Success!
        reaction = get_reaction(personality_key, result)
        
        # Check defaults if None
        if not reaction:
            reaction = "Great job! 🎉"

        # Update progress
        new_progress = await increment_progress(user_id)
        
        # Build Response
        response = f"{reaction}\n\n"
        
        # Streak check
        streak = new_progress["streak_days"]
        streak_msg = get_streak_message(streak)
        if streak_msg:
            response += f"\n🔥 *{streak} Day Streak!* {streak_msg}\n"
            
        # Badge check (every 10 tasks approx, let's use helper)
        old_tasks = user["tasks_completed"]
        new_tasks = new_progress["tasks_completed"]
        
        # Simple badge check: if new badge earned
        old_badge_name, _ = get_badge(old_tasks)
        new_badge_name, new_badge_emoji = get_badge(new_tasks)
        
        if new_badge_name != old_badge_name:
            response += f"\n🏆 *New Badge Unlocked:* {new_badge_emoji} {new_badge_name}!\n"
        
        response += f"\n📈 *Progress:* {new_tasks} tasks done."
        
        # Next Task Button & Main Menu
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        is_bilingual = (user.get("language_mode") == "bilingual")
        
        btn_next = "➡️ Следующее задание" if is_bilingual else "➡️ Next Task"
        btn_menu = "🏠 Главное меню" if is_bilingual else "🏠 Main Menu"
        
        builder.button(text=btn_next, callback_data="next_task")
        builder.button(text=btn_menu, callback_data="main_menu")
        builder.adjust(1)
        
        await message.answer(response, reply_markup=builder.as_markup(), parse_mode="Markdown")
        
    else:
        # Mistake
        reaction = get_reaction(personality_key, "mistake")
        if not reaction:
            reaction = "Not quite. Try again! 🤔"
            
        lang_mode = user.get("language_mode", "bilingual")
        tip_key = "grammar_ru" if lang_mode == "bilingual" else "grammar_en"
        tip = task_data.get(tip_key)
        
        # Fallback to English if RU tip is missing
        if not tip and lang_mode == "bilingual":
             tip = task_data.get("grammar_en")
        
        response = (
            f"{reaction}\n\n"
            f"💡 *Tip:* {tip}\n\n"
            "Try again! 💪"
        )
        await message.answer(response, parse_mode="Markdown")

import random


def get_all_grammar_tips(is_bilingual: bool):
    """Retrieve all grammar tips as a list."""
    all_tips = []
    
    # Iterate through all levels, weeks, and days
    # To keep order stable: sort keys? 
    # Python dicts preserve insertion order in recent versions, but explicit sort is safer.
    levels = ["A1", "A2", "B1", "B2", "C1"]
    
    for level_key in levels:
        weeks = CURRICULUM.get(level_key)
        if not weeks: continue
        
        for week_key in sorted(weeks.keys()):
            days = weeks[week_key]
            for day_key in sorted(days.keys()):
                data = days[day_key]
                
                tip_key = "grammar_ru" if is_bilingual else "grammar_en"
                tip = data.get(tip_key)
                # Fallback
                if not tip and is_bilingual:
                    tip = data.get("grammar_en")
                
                if tip:
                    all_tips.append(f"({level_key}) {tip}")
    return all_tips

@learning_router.message(Command("grammar"))
@learning_router.message(F.text.in_({"📖 Grammar", "📖 Грамматика"}))
@learning_router.callback_query(F.data == "menu_grammar")
async def cmd_grammar(event: types.Message | types.CallbackQuery):
    if isinstance(event, types.CallbackQuery):
        message = event.message
        user_id = event.from_user.id
        # Don't answer yet, we might replace message
    else:
        message = event
        user_id = message.from_user.id
        
    user = await get_user(user_id)
    if not user:
        if isinstance(event, types.CallbackQuery): await event.answer("Start first!")
        return

    is_bilingual = (user.get("language_mode") == "bilingual")
    all_tips = get_all_grammar_tips(is_bilingual)
    
    if not all_tips:
        text = "No grammar tips found! 🤷‍♂️"
        if isinstance(event, types.CallbackQuery):
            await event.answer(text)
        else:
            await message.answer(text)
        return
        
    # Pick random index for start
    index = random.randint(0, len(all_tips) - 1)
    
    await show_grammar_tip(message, index, all_tips, is_bilingual, is_new_message=not isinstance(event, types.CallbackQuery))
    if isinstance(event, types.CallbackQuery):
        await event.answer()

async def show_grammar_tip(message: types.Message, index: int, all_tips: list, is_bilingual: bool, is_new_message: bool = False):
    total = len(all_tips)
    # Safe index
    index = index % total
    tip = all_tips[index]
    
    title = "📖 *Случайная грамматика:*" if is_bilingual else "📖 *Random Grammar Tip:*"
    text = f"{title}\n\n{tip}\n\nTip {index + 1} of {total}"
    
    # Navigation Buttons
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    # Prev / Next
    prev_idx = (index - 1) % total
    next_idx = (index + 1) % total
    
    builder.button(text="⬅️", callback_data=f"grammar_nav_{prev_idx}")
    builder.button(text="➡️", callback_data=f"grammar_nav_{next_idx}")
    builder.button(text="🏠 Menu", callback_data="main_menu")
    
    builder.adjust(2, 1)
    
    if is_new_message:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        # Edit existing
        try:
            await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        except:
             await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@learning_router.callback_query(F.data.startswith("grammar_nav_"))
async def process_grammar_nav(callback: types.CallbackQuery):
    try:
        index = int(callback.data.split("_")[2])
    except:
        await callback.answer("Error")
        return
        
    user_id = callback.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    all_tips = get_all_grammar_tips(is_bilingual)
    
    await show_grammar_tip(callback.message, index, all_tips, is_bilingual, is_new_message=False)
    await callback.answer()

