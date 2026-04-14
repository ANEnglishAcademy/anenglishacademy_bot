import random
import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import get_user, increment_progress
from data.curriculum import CURRICULUM

games_router = Router()

class GameStates(StatesGroup):
    scramble_playing = State()
    quiz_playing = State()
    translation_playing = State()
    hangman_playing = State()
    true_false_playing = State()

@games_router.message(Command("games"))
@games_router.message(F.text.in_({"🎮 Games", "🎮 Игры"}))
@games_router.callback_query(F.data == "menu_games")
async def cmd_games_menu(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear() # Reset any active game
    
    if isinstance(event, types.CallbackQuery):
        message = event.message
        user_id = event.from_user.id
        await event.answer()
    else:
        message = event
        user_id = message.from_user.id
        
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    builder = InlineKeyboardBuilder()
    
    if is_bilingual:
        builder.button(text="🔤 Скрэмбл", callback_data="game_scramble_start")
        builder.button(text="🎯 Викторина", callback_data="game_quiz_start")
        builder.button(text="🗣️ Перевод", callback_data="game_translation_start")
        builder.button(text="🕹️ Виселица", callback_data="game_hangman_start")
        builder.button(text="⚖️ Правда / Ложь", callback_data="game_tf_start")
        builder.button(text="🏠 Меню", callback_data="main_menu")
        text = "🎮 *Игровая Зона*\nВыберите игру:"
    else:
        builder.button(text="🔤 Word Scramble", callback_data="game_scramble_start")
        builder.button(text="🎯 Grammar Quiz", callback_data="game_quiz_start")
        builder.button(text="🗣️ Translation", callback_data="game_translation_start")
        builder.button(text="🕹️ Hangman", callback_data="game_hangman_start")
        builder.button(text="⚖️ True or False", callback_data="game_tf_start")
        builder.button(text="🏠 Menu", callback_data="main_menu")
        text = "🎮 *Game Zone*\nChoose a game:"
        
    builder.adjust(1)
    
    if isinstance(event, types.Message):
         await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
         await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# --- GAME 1: WORD SCRAMBLE ---
@games_router.callback_query(F.data == "game_scramble_start")
async def start_scramble(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    # Get random word from A1-B1 curriculum keywords
    words = []
    for level_key, level_data in CURRICULUM.items():
        if level_key not in ["A1", "A2", "B1"]: continue
        if not isinstance(level_data, dict): continue
        for week_data in level_data.values():
            if not isinstance(week_data, dict): continue
            for day_data in week_data.values():
                keywords = day_data.get("keywords", [])
                topic_ru = day_data.get("topic_ru", "")
                for k in keywords:
                    clean_k = k.lower().strip()
                    if ' ' not in clean_k and len(clean_k) > 3: 
                        words.append((clean_k, topic_ru))
    
    if not words:
        await callback.answer("No words found for game!")
        return

    word, hint_ru = random.choice(words)
    scrambled_list = list(word)
    random.shuffle(scrambled_list)
    scrambled = "".join(scrambled_list)
    
    # Ensure it's not same as original
    while scrambled == word:
        random.shuffle(scrambled_list)
        scrambled = "".join(scrambled_list)
    
    await state.update_data(word=word, attempts=0)
    await state.set_state(GameStates.scramble_playing)
    
    builder = InlineKeyboardBuilder()
    if is_bilingual:
        hint_text = f"\n💡 Подсказка (Тема): {hint_ru}" if hint_ru else ""
        text = (
            f"🔤 *Скрэмбл* 🔤\n\n"
            f"Расшифруй слово: `{scrambled}`{hint_text}\n\n"
            f"Напиши ответ ниже! 👇"
        )
        builder.button(text="🏳️ Сдаюсь", callback_data="game_giveup")
    else:
        text = (
            f"🔤 *Word Scramble* 🔤\n\n"
            f"Unscramble: `{scrambled}`\n\n"
            f"Type your answer below! 👇"
        )
        builder.button(text="🏳️ Give Up", callback_data="game_giveup")
    
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@games_router.message(GameStates.scramble_playing)
async def check_scramble(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_word = data.get("word")
    user_word = message.text.strip().lower()
    
    if user_word == target_word:
        await message.answer(f"✅ Correct! The word was *{target_word}*! +1 XP 🎉", parse_mode="Markdown")
        await state.clear()
        # Offer play again
        from handlers.menu import cmd_main_menu
        await cmd_main_menu(message)
    else:
        await message.answer("❌ Try again!")

# --- GAME 2: GRAMMAR QUIZ ---
@games_router.callback_query(F.data == "game_quiz_start")
async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    # Select a random task that has grammar_en/ru
    # Generate 1 correct answer (task) and 3 distractors? 
    # Or just True/False? 
    # Let's do simple: "Is this sentence correct?" or "Fill in the blank"
    # Actually, simpler: "What is the grammar rule for this topic?" -> Multiple choice? Hard to generate.
    # Let's do: "Translate this word" (easier) -> No that's translation game.
    # Grammar Quiz: "Choose the correct form."
    
    # 1. Pick a sentence from tasks and blank out a keyword.
    user_id = callback.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    # Find valid task
    import re
    tasks = []
    all_keywords_in_level = []
    for level_key, weeks in CURRICULUM.items():
        if level_key not in ["A1", "A2", "B1"]: continue
        if not isinstance(weeks, dict): continue
        for week_data in weeks.values():
            if not isinstance(week_data, dict): continue
            for day_data in week_data.values():
                task = day_data.get('task')
                task_ru = day_data.get('task_ru')
                keywords = day_data.get('keywords', [])
                if task and keywords:
                    tasks.append((task, task_ru, keywords[0])) # Take first keyword as target
                    all_keywords_in_level.extend(keywords)
                    
    if not tasks:
        await callback.answer("No quiz data.")
        return
        
    sentence, sentence_ru, key = random.choice(tasks)
    
    # Create blank
    if key in sentence:
        question = sentence.replace(key, "_____")
    else:
        # Keyword might be different case or form
        insens_key = re.escape(key)
        question = re.sub(f'(?i){insens_key}', '_____', sentence)
        if question == sentence:
            # Fallback Retry
            await start_quiz(callback, state)
            return

    # Generate options
    correct = key
    distractors = [k for k in all_keywords_in_level if k.lower() != correct.lower()]
    distractors = list(set(distractors))
    if len(distractors) < 3:
        distractors.extend(["apple", "run", "blue"])
    distractors = random.sample(distractors, 3)
    options = [correct] + distractors
    random.shuffle(options)
    
    await state.update_data(correct_option=correct)
    await state.set_state(GameStates.quiz_playing)
    
    builder = InlineKeyboardBuilder()
    for opt in options:
        builder.button(text=opt, callback_data=f"quiz_ans_{opt}")
    
    builder.adjust(2)
    
    msg = (
        f"🎯 *Grammar Quiz*\n\n"
        f"Complete the sentence:\n"
        f"*{question}*"
    )
    if is_bilingual:
        hint_text = f"\n\n🇷🇺 *Перевод для контекста:*\n{sentence_ru}" if sentence_ru else ""
        msg = (
            f"🎯 *Викторина*\n\n"
            f"Дополни предложение:\n"
            f"*{question}*{hint_text}"
        )
        
    await callback.message.edit_text(msg, reply_markup=builder.as_markup(), parse_mode="Markdown")

@games_router.callback_query(GameStates.quiz_playing, F.data.startswith("quiz_ans_"))
async def check_quiz(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    correct = data.get("correct_option")
    answer = callback.data.split("_", 2)[2]
    
    if answer == correct:
        await callback.message.edit_text(f"✅ Correct! *{correct}* fits perfectly!", parse_mode="Markdown")
    else:
        await callback.message.edit_text(f"❌ Wrong! The correct answer was *{correct}*.", parse_mode="Markdown")
        
    await state.clear()
    # Offer main menu or replay logic here (simplified for now)
    
# --- GAME 3: TRANSLATION CHALLENGE ---
@games_router.callback_query(F.data == "game_translation_start")
async def start_translation(callback: types.CallbackQuery, state: FSMContext):
    # Pick a random keyword, user must translate it to Russian (if bilingual) or English definition?
    # Since we don't have definitions in DB, assume Bilingual mode is target.
    # If English mode, maybe translate RU->EN? We have topic_ru.
    
    user_id = callback.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    if not is_bilingual:
        await callback.answer("This game is best for Bilingual mode!", show_alert=True)
        # Continue anyway?
        
    # We need a pair: EN word -> RU translation.
    # We don't have a dictionary in DB.
    # We have topic -> topic_ru.
    
    pairs = []
    for level_key, weeks in CURRICULUM.items():
        if level_key not in ["A1", "A2", "B1"]: continue
        if not isinstance(weeks, dict): continue
        for week_data in weeks.values():
            if not isinstance(week_data, dict): continue
            for day_data in week_data.values():
                en = day_data.get('topic')
                ru = day_data.get('topic_ru')
                if en and ru:
                    pairs.append((en, ru))
                    
    if not pairs:
        await callback.answer("No translation data.")
        return
        
    en, ru = random.choice(pairs)
    
    # 50% chance to ask EN->RU or RU->EN
    direction = random.choice(["en_ru", "ru_en"])
    
    if direction == "en_ru": # Show EN, ask RU
        target = ru
        prompt = f"Переведи на русский:\n🇺🇸 *{en}* ➡️ 🇷🇺 ?"
    else: # Show RU, ask EN
        target = en
        prompt = f"Переведи на английский:\n🇷🇺 *{ru}* ➡️ 🇺🇸 ?"
        
    await state.update_data(target=target)
    await state.set_state(GameStates.translation_playing)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏳️ Сдаюсь / Give Up", callback_data="game_giveup")
    
    await callback.message.edit_text(
        f"🗣️ *Испытание Переводом (Translation)*\n\n{prompt}\n\nНапиши перевод!",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@games_router.message(GameStates.translation_playing)
async def check_translation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target = data.get("target").lower()
    user_ans = message.text.strip().lower()
    
    # Simple fuzzy match or exact? Exact for now.
    if user_ans == target:
        await message.answer("✅ Correct!", parse_mode="Markdown")
        await state.clear()
        from handlers.menu import cmd_main_menu
        await cmd_main_menu(message)
    else:
        # Check similarity?
        await message.answer(f"❌ Incorrect. Try again!")

# --- GAME 4: HANGMAN ---
@games_router.callback_query(F.data == "game_hangman_start")
async def start_hangman(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    words = []
    for level_key, level_data in CURRICULUM.items():
        if level_key not in ["A1", "A2", "B1"]: continue
        if not isinstance(level_data, dict): continue
        for week_data in level_data.values():
            if not isinstance(week_data, dict): continue
            for day_data in week_data.values():
                keywords = day_data.get("keywords", [])
                topic_ru = day_data.get("topic_ru", "")
                for k in keywords:
                    clean_k = k.lower().strip()
                    if ' ' not in clean_k and clean_k.isalpha() and len(clean_k) >= 3: 
                        words.append((clean_k, topic_ru))
                        
    if not words:
        await callback.answer("No words found for game!")
        return

    word, hint_ru = random.choice(words)
    
    await state.update_data(word=word, guessed="", lives=6, hint_ru=hint_ru)
    await state.set_state(GameStates.hangman_playing)
    
    hidden = " ".join(["_" for _ in word])
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏳️ Сдаюсь / Give Up", callback_data="game_giveup")
    
    if is_bilingual:
        hint_text = f"\n💡 Подсказка (Тема): {hint_ru}" if hint_ru else ""
        msg = f"🕹️ *Виселица (Hangman)*\n\nСлово: `{hidden}`\nОсталось попыток: 6{hint_text}\n\nОтправь ОДНУ букву, чтобы угадать!"
    else:
        msg = f"🕹️ *Hangman*\n\nWord: `{hidden}`\nLives left: 6\n\nSend ONE letter to guess!"
        
    await callback.message.edit_text(msg, reply_markup=builder.as_markup(), parse_mode="Markdown")

@games_router.message(GameStates.hangman_playing)
async def check_hangman(message: types.Message, state: FSMContext):
    guess = message.text.strip().lower()
    
    data = await state.get_data()
    word = data.get("word")
    guessed = data.get("guessed", "")
    lives = data.get("lives", 6)
    hint_ru = data.get("hint_ru", "")
    
    user_id = message.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    # Validation
    if len(guess) != 1 or not guess.isalpha():
        # They might have typed the full word
        if guess == word:
            await message.answer(f"🎉 Правильно! Слово: *{word}*! +1 XP" if is_bilingual else f"🎉 Correct! The word was *{word}*! +1 XP", parse_mode="Markdown")
            await state.clear()
            from handlers.menu import cmd_main_menu
            await cmd_main_menu(message)
            return
        else:
            await message.answer("⚠️ Пожалуйста, отправь ровно ОДНУ английскую букву." if is_bilingual else "⚠️ Please send exactly ONE English letter.")
            return

    if guess in guessed:
         await message.answer("⚠️ Ты уже называл эту букву!" if is_bilingual else "⚠️ You already guessed this letter!")
         return
         
    guessed += guess
    
    if guess not in word:
        lives -= 1
        
    await state.update_data(guessed=guessed, lives=lives)
    
    hidden = " ".join([char if char in guessed else "_" for char in word])
    
    if lives <= 0:
        await message.answer(f"💀 Вы проиграли! Слово было: *{word}*" if is_bilingual else f"💀 Game Over! The word was: *{word}*", parse_mode="Markdown")
        await state.clear()
        from handlers.menu import cmd_main_menu
        await cmd_main_menu(message)
        return
        
    if "_" not in hidden:
        await message.answer(f"🎉 Вы выиграли! Слово: *{word}*! +1 XP" if is_bilingual else f"🎉 You win! The word is: *{word}*! +1 XP", parse_mode="Markdown")
        await state.clear()
        from handlers.menu import cmd_main_menu
        await cmd_main_menu(message)
        return
        
    builder = InlineKeyboardBuilder()
    builder.button(text="🏳️ Сдаюсь / Give Up", callback_data="game_giveup")

    if is_bilingual:
        hint_text = f"\n💡 Подсказка (Тема): {hint_ru}" if hint_ru else ""
        msg = f"🕹️ *Виселица (Hangman)*\n\nСлово: `{hidden}`\nОсталось попыток: {lives}{hint_text}\n\nОтправь следующую букву!"
    else:
        msg = f"🕹️ *Hangman*\n\nWord: `{hidden}`\nLives left: {lives}\n\nSend next letter!"
        
    await message.answer(msg, reply_markup=builder.as_markup(), parse_mode="Markdown")

# --- GAME 5: TRUE OR FALSE ---
@games_router.callback_query(F.data == "game_tf_start")
async def start_true_false(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    topics = []
    for level_key, weeks in CURRICULUM.items():
        if level_key not in ["A1", "A2", "B1"]: continue
        if not isinstance(weeks, dict): continue
        for week_data in weeks.values():
            if not isinstance(week_data, dict): continue
            for day_data in week_data.values():
                en = day_data.get('topic')
                ru = day_data.get('topic_ru')
                if en and ru:
                    topics.append((en, ru))
                    
    if not topics:
        await callback.answer("No data found!")
        return
        
    en, correct_ru = random.choice(topics)
    
    is_true = random.choice([True, False])
    
    if is_true:
        shown_ru = correct_ru
    else:
        # Pick a different topic_ru
        distractor = random.choice([t[1] for t in topics if t[1] != correct_ru])
        shown_ru = distractor
        
    await state.update_data(tf_correct=is_true, en_topic=en)
    await state.set_state(GameStates.true_false_playing)
    
    builder = InlineKeyboardBuilder()
    if is_bilingual:
        builder.button(text="✅ Правда", callback_data="tf_ans_true")
        builder.button(text="❌ Ложь", callback_data="tf_ans_false")
        msg = f"⚖️ *Правда или Ложь*\n\nПравильный ли это перевод темы?\n\n🇺🇸 *{en}*\n🇷🇺 *{shown_ru}*"
    else:
        builder.button(text="✅ True", callback_data="tf_ans_true")
        builder.button(text="❌ False", callback_data="tf_ans_false")
        msg = f"⚖️ *True or False*\n\nIs this translation correct?\n\n🇺🇸 *{en}*\n🇷🇺 *{shown_ru}*"
        
    builder.adjust(2)
    
    await callback.message.edit_text(msg, reply_markup=builder.as_markup(), parse_mode="Markdown")

@games_router.callback_query(GameStates.true_false_playing, F.data.startswith("tf_ans_"))
async def check_true_false(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    is_true = data.get("tf_correct")
    en_topic = data.get("en_topic")
    
    user_id = callback.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    ans = callback.data.split("_")[2] # "true" or "false"
    user_guess = (ans == "true")
    
    await state.clear()
    
    if user_guess == is_true:
        msg = f"🎉 *Правильно!* +1 XP\nTopic: '{en_topic}'" if is_bilingual else f"🎉 *Correct!* +1 XP\nTopic: '{en_topic}'"
        await callback.message.edit_text(msg, parse_mode="Markdown")
    else:
        msg = f"❌ *Неверно!* Topic: '{en_topic}'\n{ 'Перевод был правильным!' if is_true else 'Это был неправильный перевод.'}" if is_bilingual else f"❌ *Wrong!*\n{ 'It was true!' if is_true else 'It was false!'}"
        await callback.message.edit_text(msg, parse_mode="Markdown")

# Global Give Up
@games_router.callback_query(F.data == "game_giveup")
async def game_giveup(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    word = data.get("word") or data.get("target") or "Unknown"
    
    user_id = callback.from_user.id
    user = await get_user(user_id)
    is_bilingual = (user.get("language_mode") == "bilingual")
    
    msg = f"🏳️ Игра окончена. Правильный ответ: *{word}*" if is_bilingual else f"🏳️ Game Over. The correct answer was: *{word}*"
    
    await callback.message.edit_text(msg, parse_mode="Markdown")
    await state.clear()
