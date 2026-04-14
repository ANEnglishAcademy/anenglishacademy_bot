import logging
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.states import OnboardingStates
from database.db import create_user, get_user, update_user, add_referral
from data.personalities import PERSONALITIES

onboarding_router = Router()

@onboarding_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if user:
        from handlers.menu import cmd_main_menu
        await cmd_main_menu(message)
        return

    # Parse potential referral like /start ref12345
    args = message.text.split(" ")
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref"):
        try:
            referrer_id = int(args[1][3:])
        except ValueError:
            pass

    # New user: Start onboarding
    await create_user(user_id)
    
    # Process referral
    if referrer_id and referrer_id != user_id:
        success = await add_referral(user_id, referrer_id)
        if success:
            try:
                await message.bot.send_message(
                    chat_id=referrer_id, 
                    text="🎉 *Someone just joined using your invite link!*\nThank you for spreading the word!",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logging.error(f"Failed to send referral notification to {referrer_id}: {e}")
    
    # Step 1: Ask for Language Mode FIRST
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇸 English Only", callback_data="lang_english")
    builder.button(text="🇷🇺 English + Русский", callback_data="lang_bilingual")
    builder.adjust(1)

    await message.answer(
        "👋 Welcome to AN English Academy!\n"
        "Добро пожаловать в AN English Academy! 🎓\n\n"
        "How would you like to learn?\n"
        "Как вы хотите учиться?\n\n"
        "🇺🇸 *English Only* — everything in English\n"
        "🇷🇺 *English + Русский* — tips & grammar explained in Russian\n"
        "     (подсказки и грамматика на русском)",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await state.set_state(OnboardingStates.choosing_language)

@onboarding_router.callback_query(OnboardingStates.choosing_language, F.data.startswith("lang_"))
async def process_language(callback: types.CallbackQuery, state: FSMContext):
    lang_mode = callback.data.split("_")[1]  # "english" or "bilingual"
    user_id = callback.from_user.id
    await update_user(user_id, language_mode=lang_mode)
    
    is_bilingual = lang_mode == "bilingual"
    
    # Step 2: Ask for Level
    builder = InlineKeyboardBuilder()
    levels = ["A1", "A2", "B1", "B2", "C1"]
    for level in levels:
        builder.button(text=level, callback_data=f"level_{level}")
    builder.adjust(3)

    if is_bilingual:
        text = (
            "✅ Отлично! Подсказки будут на русском 🇷🇺\n\n"
            "Now, choose your English level:\n"
            "Выберите ваш уровень английского:"
        )
    else:
        text = "✅ English mode activated!\n\nNow, choose your English level:"

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await state.set_state(OnboardingStates.choosing_level)

@onboarding_router.callback_query(OnboardingStates.choosing_level, F.data.startswith("level_"))
async def process_level(callback: types.CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    user_id = callback.from_user.id
    await update_user(user_id, level=level)
    
    # Step 3: Ask for Personality
    builder = InlineKeyboardBuilder()
    for key, data in PERSONALITIES.items():
        builder.button(text=f"{data['emoji']} {data['name']}", callback_data=f"pers_{key}")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"Level set to *{level}*! ✅\n\n"
        "Now, choose your teacher's personality:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await state.set_state(OnboardingStates.choosing_personality)

@onboarding_router.callback_query(OnboardingStates.choosing_personality, F.data.startswith("pers_"))
async def process_personality(callback: types.CallbackQuery, state: FSMContext):
    personality = callback.data.split("_")[1]
    user_id = callback.from_user.id
    await update_user(user_id, personality=personality)

    # 4. Ask for Focus
    builder = InlineKeyboardBuilder()
    focus_areas = {
        "speaking": "🗣️ Speaking",
        "writing": "✍️ Writing",
        "vocabulary": "📖 Vocabulary",
        "listening": "🎧 Listening",
        "fun": "🎮 Fun & Games"
    }
    for key, label in focus_areas.items():
        builder.button(text=label, callback_data=f"focus_{key}")
    builder.adjust(2)

    await callback.message.edit_text(
        f"Awesome! Teacher set to *{PERSONALITIES[personality]['name']}*. 🎓\n\n"
        "What is your main focus?",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await state.set_state(OnboardingStates.choosing_focus)

@onboarding_router.callback_query(OnboardingStates.choosing_focus, F.data.startswith("focus_"))
async def process_focus(callback: types.CallbackQuery, state: FSMContext):
    focus = callback.data.split("_")[1]
    user_id = callback.from_user.id
    await update_user(user_id, focus=focus)
    
    # 5. Ask for Nickname
    await callback.message.edit_text(
        f"Got it! We'll focus on *{focus.capitalize()}*. 🎯\n\n"
        "Finally, what should I call you? (Type your nickname below 👇)",
        parse_mode="Markdown"
    )
    await state.set_state(OnboardingStates.typing_nickname)

@onboarding_router.message(OnboardingStates.typing_nickname, F.text)
async def process_nickname(message: types.Message, state: FSMContext):
    nickname = message.text.strip()
    if len(nickname) > 20:
        await message.answer("Please keep it under 20 characters. Try again!")
        return
        
    user_id = message.from_user.id
    await update_user(user_id, nickname=nickname, onboarding_complete=1)
    
    user = await get_user(user_id)
    personality_key = user["personality"]
    greeting = PERSONALITIES.get(personality_key, {}).get("greeting", "Welcome!")
    
    await message.answer(
        f"Nice to meet you, *{nickname}*! 🎉\n\n{greeting}"
    )
    
    from handlers.menu import cmd_main_menu
    await cmd_main_menu(message)
    await state.clear()
