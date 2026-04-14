from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db import get_user

menu_router = Router()

@menu_router.message(Command("menu"))
@menu_router.callback_query(F.data == "main_menu")
async def cmd_main_menu(event: types.Message | types.CallbackQuery):
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

    is_bilingual = (user.get("language_mode") == "bilingual")
    
    builder = InlineKeyboardBuilder()
    
    # Row 1: Task & Profile
    if is_bilingual:
        builder.button(text="📚 Задание", callback_data="menu_task")
        builder.button(text="👤 Профиль", callback_data="menu_profile")
    else:
        builder.button(text="📚 Solve Task", callback_data="menu_task")
        builder.button(text="👤 My Profile", callback_data="menu_profile")
    
    # Row 2: Settings & Help
    if is_bilingual:
        builder.button(text="⚙️ Настройки", callback_data="settings_main")
        builder.button(text="🆘 Помощь", callback_data="menu_help")
    else:
        builder.button(text="⚙️ Settings", callback_data="settings_main")
        builder.button(text="🆘 Help", callback_data="menu_help")
        
    # Row 3: Grammar & Games
    if is_bilingual:
        builder.button(text="📖 Грамматика", callback_data="menu_grammar")
        builder.button(text="🎮 Игры", callback_data="menu_games")
    else:
        builder.button(text="📖 Grammar Tip", callback_data="menu_grammar")
        builder.button(text="🎮 Games", callback_data="menu_games")
        
    builder.adjust(2, 2, 2)
    
    text = (
        "🏠 *Главное Меню*\n"
        "Выберите действие:" 
        if is_bilingual else 
        "🏠 *Main Menu*\n"
        "Choose an action:"
    )
    
    if isinstance(event, types.Message):
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
