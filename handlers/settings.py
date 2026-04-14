import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import update_user, get_user
from data.personalities import PERSONALITIES

settings_router = Router()

import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import update_user, get_user
from data.personalities import PERSONALITIES

settings_router = Router()

# --- Main Settings Menu ---
@settings_router.message(Command("settings"))
@settings_router.message(F.text.in_({"⚙️ Settings", "⚙️ Настройки"}))
@settings_router.callback_query(F.data == "settings_main")
async def cmd_settings(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    user = await get_user(user_id)
    lang_mode = user.get("language_mode", "english")
    is_bilingual = (lang_mode == "bilingual")

    builder = InlineKeyboardBuilder()
    
    if is_bilingual:
        builder.button(text="📊 Уровень", callback_data="settings_level")
        builder.button(text="🤖 Учитель", callback_data="settings_personality")
        builder.button(text="🎯 Фокус", callback_data="settings_focus")
        builder.button(text="🌐 Язык", callback_data="settings_language")
        builder.button(text="📝 Никнейм", callback_data="settings_nickname")
        text = "⚙️ *Настройки*\n\nВыберите, что хотите изменить:"
    else:
        builder.button(text="📊 Level", callback_data="settings_level")
        builder.button(text="🤖 Teacher", callback_data="settings_personality")
        builder.button(text="🎯 Focus", callback_data="settings_focus")
        builder.button(text="🌐 Language", callback_data="settings_language")
        builder.button(text="📝 Nickname", callback_data="settings_nickname")
        text = "⚙️ *Settings Menu*\n\nChoose what you would like to change:"

    builder.adjust(2)
    markup = builder.as_markup()
    
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await event.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

# --- Sub-menus (Callbacks) ---

@settings_router.callback_query(F.data == "settings_level")
async def menu_level(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    is_bilingual = (user.get("language_mode") == "bilingual")

    builder = InlineKeyboardBuilder()
    levels = ["A1", "A2", "B1", "B2", "C1"]
    for level in levels:
        builder.button(text=level, callback_data=f"set_level_{level}")
    builder.adjust(3)
    
    text = "📊 Выберите ваш уровень:" if is_bilingual else "📊 Select your new English level:"
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@settings_router.callback_query(F.data == "settings_personality")
async def menu_personality(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    is_bilingual = (user.get("language_mode") == "bilingual")

    builder = InlineKeyboardBuilder()
    for key, data in PERSONALITIES.items():
        builder.button(text=f"{data['emoji']} {data['name']}", callback_data=f"set_pers_{key}")
    builder.adjust(1)
    
    text = "🤖 Выберите характер учителя:" if is_bilingual else "🤖 Choose your new teacher personality:"
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@settings_router.callback_query(F.data == "settings_language")
async def menu_language(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    is_bilingual = (user.get("language_mode") == "bilingual")

    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇸 English Only", callback_data="set_lang_english")
    builder.button(text="🇷🇺 English + Русский", callback_data="set_lang_bilingual")
    builder.adjust(1)
    
    if is_bilingual:
        text = "🌐 Выберите режим обучения:"
    else:
        text = "🌐 Choose your language mode:\nВыберите режим обучения:"
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@settings_router.callback_query(F.data == "settings_nickname")
async def menu_nickname(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    if is_bilingual:
        text = "📝 Чтобы сменить имя, отправьте команду:\n\n`/setnickname ВашеИмя`"
    else:
        text = "📝 To change your nickname, please send the command:\n\n`/setnickname YourName`"

    await callback.message.edit_text(text, parse_mode="Markdown")

@settings_router.callback_query(F.data == "settings_focus")
async def menu_focus(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    is_bilingual = (user.get("language_mode") == "bilingual")

    builder = InlineKeyboardBuilder()
    focus_areas = {
        "speaking": "🗣️ Speaking",
        "writing": "✍️ Writing",
        "vocabulary": "📖 Vocabulary",
        "listening": "🎧 Listening",
        "fun": "🎮 Fun & Games"
    }
    for key, label in focus_areas.items():
        builder.button(text=label, callback_data=f"set_focus_{key}")
    builder.adjust(2)
    
    text = "🎯 Выберите ваш фокус:" if is_bilingual else "🎯 Choose your main focus:"
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


# --- Actions (Processing Choices) ---

@settings_router.callback_query(F.data.startswith("set_level_"))
async def process_setlevel(callback: types.CallbackQuery):
    level = callback.data.split("_")[2]
    user_id = callback.from_user.id
    await update_user(user_id, level=level)
    
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    msg = f"✅ Уровень обновлен до *{level}*!" if is_bilingual else f"✅ Level updated to *{level}*!"
    await callback.message.edit_text(msg, parse_mode="Markdown")

@settings_router.callback_query(F.data.startswith("set_focus_"))
async def process_setfocus(callback: types.CallbackQuery):
    focus = callback.data.split("_")[2]
    user_id = callback.from_user.id
    await update_user(user_id, focus=focus)
    
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    msg = f"✅ Фокус изменен на *{focus.capitalize()}*!" if is_bilingual else f"✅ Focus updated to *{focus.capitalize()}*!"
    await callback.message.edit_text(msg, parse_mode="Markdown")

@settings_router.callback_query(F.data.startswith("set_pers_"))
async def process_setpersonality(callback: types.CallbackQuery):
    personality = callback.data.split("_")[2]
    user_id = callback.from_user.id
    name = PERSONALITIES.get(personality, {}).get("name", personality)
    await update_user(user_id, personality=personality)
    
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    msg = f"✅ Учитель теперь *{name}*!" if is_bilingual else f"✅ Teacher changed to *{name}*!"
    await callback.message.edit_text(msg, parse_mode="Markdown")

@settings_router.callback_query(F.data.startswith("set_lang_"))
async def process_setlanguage(callback: types.CallbackQuery):
    lang = callback.data.split("_")[2]
    user_id = callback.from_user.id
    await update_user(user_id, language_mode=lang)
    
    # We always use the target language for confirmation
    if lang == "bilingual":
        msg = "✅ Язык изменен! Подсказки будут на русском. 🇷🇺"
    else:
        msg = "✅ Language updated! English mode activated. 🇺🇸"
        
    await callback.message.edit_text(msg, parse_mode="Markdown")

# --- Legacy/Direct Commands (Keep for convenience) ---

@settings_router.message(Command("setlevel"))
async def cmd_setlevel(message: types.Message):
    await cmd_settings(message) # Redirect to main settings for simplicity or keep separate? Let's just redirect to menu or show level menu directly.
    # Showing level menu directly:
    builder = InlineKeyboardBuilder()
    levels = ["A1", "A2", "B1", "B2", "C1"]
    for level in levels:
        builder.button(text=level, callback_data=f"set_level_{level}")
    builder.adjust(3)
    await message.answer("Select your new English level:", reply_markup=builder.as_markup())

@settings_router.message(Command("personality"))
async def cmd_personality(message: types.Message):
    builder = InlineKeyboardBuilder()
    for key, data in PERSONALITIES.items():
        builder.button(text=f"{data['emoji']} {data['name']}", callback_data=f"set_pers_{key}")
    builder.adjust(1)
    await message.answer("Choose your new teacher personality:", reply_markup=builder.as_markup())

@settings_router.message(Command("setnickname"))
async def cmd_setnickname(message: types.Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.answer("⚠️ Usage: `/setnickname YourName`", parse_mode="Markdown")
        return
        
    nickname = parts[1].strip()[:20]
    user_id = message.from_user.id
    
    await update_user(user_id, nickname=nickname)
    await message.answer(f"✅ Nickname updated to *{nickname}*!", parse_mode="Markdown")
