"""
Utility helpers: badges, progress bars, streak messages, answer evaluation.
"""

import random


# ─── Badge System ────────────────────────────────────────────────
BADGES = [
    (0, "🌱", "Seedling"),
    (5, "🥉", "Bronze Learner"),
    (10, "🥈", "Rising Star"),
    (20, "🥇", "Pro"),
    (50, "🏆", "Legend"),
    (100, "💎", "Diamond"),
]


def get_badge(tasks_completed: int) -> tuple[str, str]:
    """Return (emoji, name) for the current badge."""
    badge = BADGES[0]
    for threshold, emoji, name in BADGES:
        if tasks_completed >= threshold:
            badge = (emoji, name)
    return badge


def get_next_badge_info(tasks_completed: int) -> tuple[int, str, str] | None:
    """Return (threshold, emoji, name) for the NEXT badge, or None if maxed."""
    for threshold, emoji, name in BADGES:
        if tasks_completed < threshold:
            return (threshold, emoji, name)
    return None


# ─── Progress Bar ────────────────────────────────────────────────
def get_progress_bar(tasks_completed: int, bar_length: int = 10) -> str:
    """Visual progress bar toward the next badge."""
    next_badge = get_next_badge_info(tasks_completed)
    if not next_badge:
        return "████████████ MAX LEVEL! 💎"

    target = next_badge[0]
    # Find previous threshold
    prev = 0
    for threshold, _, _ in BADGES:
        if threshold <= tasks_completed:
            prev = threshold
    progress = tasks_completed - prev
    total = target - prev
    filled = int((progress / total) * bar_length) if total > 0 else bar_length
    empty = bar_length - filled
    return f"[{'█' * filled}{'░' * empty}] {progress}/{total} → {next_badge[1]} {next_badge[2]}"


# ─── Streak Messages ────────────────────────────────────────────
STREAK_MILESTONES = {
    3: "🔥 3-day streak! You're on fire!",
    7: "⚡ 7-day streak! Unstoppable!",
    14: "🌟 2-week streak! You're a machine!",
    30: "🏅 1-month streak! Absolute legend!",
    60: "👑 2-month streak! Hall of Fame!",
    100: "💎 100-day streak! You ARE English!",
}


def get_streak_message(streak: int) -> str | None:
    """Return a celebration message if the streak hits a milestone."""
    return STREAK_MILESTONES.get(streak)


# ─── Answer Evaluation ──────────────────────────────────────────
def evaluate_answer(user_text: str, keywords: list[str]) -> str:
    """
    Basic keyword-based answer evaluation.
    Returns: 'correct', 'mistake', or 'funny'
    """
    text_lower = user_text.lower().strip()

    # Check if it's very short or just emoji (probably funny/creative)
    if len(text_lower) < 3:
        return "mistake"

    # Check for keywords
    matched = sum(1 for kw in keywords if kw.lower() in text_lower)

    if matched >= 1:
        # Check for extra creativity (long or has emojis/exclamation)
        has_flair = (
            len(text_lower) > 40
            or "!" in user_text
            or any(ord(c) > 0x1F600 for c in user_text)
        )
        if has_flair and random.random() > 0.5:
            return "funny"
        return "correct"

    return "mistake"


# ─── Simple EN→RU Dictionary ────────────────────────────────────
DICTIONARY = {
    "weird": "странный, необычный",
    "awkward": "неловкий, неуклюжий",
    "cool": "классный, крутой",
    "awesome": "потрясающий, бомбический",
    "stubborn": "упрямый, настойчивый",
    "chill": "расслабленный; расслабиться",
    "dude": "чувак, парень",
    "vibe": "атмосфера, настроение",
    "literally": "буквально",
    "basically": "по сути, в основном",
    "random": "случайный, рандомный",
    "gorgeous": "великолепный, шикарный",
    "challenge": "вызов, испытание",
    "struggle": "бороться, борьба",
    "huge": "огромный",
    "tiny": "крошечный",
    "grumpy": "ворчливый",
    "clumsy": "неуклюжий",
    "hilarious": "смешной, уморительный",
    "sarcastic": "саркастичный",
    "exhausted": "измотанный, уставший",
    "annoying": "раздражающий",
    "stunning": "потрясающий, сногсшибательный",
    "ridiculous": "нелепый, абсурдный",
    "brilliant": "блестящий, гениальный",
    "creepy": "жуткий, пугающий",
    "messy": "беспорядочный, грязный",
    "fancy": "модный, причудливый",
    "sneaky": "хитрый, подлый",
    "brave": "смелый, храбрый",
    "lazy": "ленивый",
    "curious": "любопытный",
    "polite": "вежливый",
    "rude": "грубый",
    "generous": "щедрый",
    "selfish": "эгоистичный",
    "patient": "терпеливый",
    "reliable": "надёжный",
    "ambitious": "амбициозный",
    "confident": "уверенный",
    "shy": "стеснительный, робкий",
    "honest": "честный",
    "meanwhile": "тем временем",
    "however": "однако",
    "although": "хотя",
    "therefore": "поэтому, следовательно",
    "nevertheless": "тем не менее",
    "moreover": "более того, кроме того",
    "despite": "несмотря на",
    "apparently": "очевидно, по-видимому",
    "eventually": "в конце концов",
    "immediately": "немедленно",
    "obviously": "очевидно",
    "recently": "недавно",
    "suddenly": "вдруг, внезапно",
    "generally": "обычно, в целом",
    "probably": "вероятно, наверное",
    "definitely": "определённо, точно",
    "actually": "на самом деле",
    "give up": "сдаться",
    "turn on": "включить",
    "turn off": "выключить",
    "put off": "отложить",
    "come across": "наткнуться, встретить",
    "break the ice": "растопить лёд, начать общение",
    "take off": "взлетать; снимать (одежду)",
    "figure out": "разобраться, понять",
    "look forward to": "с нетерпением ждать",
    "run out of": "закончиться (о ресурсе)",
    "get along": "ладить",
    "make up": "помириться; выдумать",
    "show off": "хвастаться",
    "work out": "тренироваться; разобраться",
    "hang out": "тусоваться, проводить время",
}


def translate_word(word: str) -> str | None:
    """Look up a word in the built-in EN→RU dictionary."""
    return DICTIONARY.get(word.lower().strip())


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu(is_bilingual: bool = False) -> ReplyKeyboardMarkup:
    """Returns the persistent main menu keyboard."""
    if is_bilingual:
        keyboard = [
            [KeyboardButton(text="📚 Задание"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="🆘 Помощь")]
        ]
    else:
        keyboard = [
            [KeyboardButton(text="📚 Task"), KeyboardButton(text="👤 Profile")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="🆘 Help")]
        ]
        
    kb = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    return kb
