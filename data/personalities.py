"""
5 Bot Personality reaction templates.
Each personality has: name, emoji, greeting, and reaction lists for correct/mistake/funny.
All reactions are in American English with the specified character voice.
"""

import random

PERSONALITIES = {
    "rockstar": {
        "name": "Rockstar Teacher",
        "emoji": "🎸",
        "greeting": "YEAH! You picked me — the loudest, wildest teacher alive! Let's melt some grammar! 🤘🔥",
        "correct": [
            "🎸 YEAH, BABY!!! Crowd goes wild! You SMASHED that grammar solo! 🎤🔥",
            "🤘 NAILED IT! That was a killer line, superstar! The crowd is on their feet!",
            "🎶 OH YEAH! Perfect execution! You're rockin' English like a BOSS!",
            "🔥 HECK YEAH!!! You crushed it! Standing ovation, dude!",
            "🎤 WOOO! That answer was pure GOLD! Encore, encore!",
            "🤘 EPIC! You just dropped a grammar bomb! BOOM! 💥",
        ],
        "mistake": [
            "🎸 Ouch… wrong chord, buddy. Even my guitar facepalmed. Try again! 😬",
            "😬 Oof… that's off-key, dude. Let me show you the right riff…",
            "🎸 NOPE! That note was flat. Here's how to shred it properly:",
            "😤 Wrong solo, bro! But hey, even rock stars mess up. Here's the fix:",
            "🎶 Oops! That lyric ain't right. Let's remix it:",
        ],
        "funny": [
            "🤣 HAHAHA! That's SO WILD — I'd put it on my next album! 🎶",
            "😂 LOL, dude! That's insane — but grammatically? ROCK SOLID! 🤘",
            "🎸 WHOA! That's the weirdest thing I've read today… and I LOVE IT!",
            "🤣 Bro! My guitar just laughed. That was LEGENDARY!",
            "😂 That's so crazy, it deserves its own music video! Grammar's on point too! 🎬",
        ],
        "streak": "🔥 {streak}-day streak?! You're on a WORLD TOUR, baby! Keep rockin'!",
        "badge": "🏅 NEW BADGE: {badge}! The crowd throws roses! You're a LEGEND!",
    },
    "hippie": {
        "name": "Hippie Guru",
        "emoji": "🌻",
        "greeting": "Peace and love, friend ✌️ I'm your chill English guru. Let the language flow through you like a cosmic river 🌊",
        "correct": [
            "🌞 Beautiful, my friend! Your English shines like the morning sun.",
            "✌️ Groovy, man! Your grammar flows like a peaceful river.",
            "🌻 Yes! That sentence is pure harmony. The universe approves!",
            "☮️ Wonderful energy! Your English vibes are perfectly aligned.",
            "🌈 That answer radiates positivity and correctness, friend!",
        ],
        "mistake": [
            "🌌 Your heart is pure, but your verb tense… is lost in the universe. Let's realign it.",
            "🌊 Hmm, the energy feels off… your grammar needs a little realignment, man.",
            "🌻 Your soul is free, but your sentence is trapped in the wrong tense. Let's free it:",
            "☮️ Peace, friend. That's not quite right. Let me guide your words gently:",
        ],
        "funny": [
            "✌️ Your creativity flows like cosmic vibes, man. I dig it!",
            "🌈 WHOA! That answer is like a psychedelic trip — wild AND correct!",
            "🌻 Man, that's far out! Your imagination is a beautiful flower blooming!",
            "😂 Haha, you're a free spirit, dude! And your grammar? Totally groovy!",
        ],
        "streak": "🌻 {streak} days of flowing English! Your cosmic energy is UNSTOPPABLE!",
        "badge": "✨ NEW BADGE: {badge}! Your inner light is getting brighter, friend!",
    },
    "grandma": {
        "name": "English Grandma",
        "emoji": "👵",
        "greeting": "Hello, sweetheart! 🍪 I'm your English Grandma. I'll teach you proper English — and bake you cookies when you do well!",
        "correct": [
            "🍪 Good job, sugarplum! You'd make me proud at the church bingo night!",
            "💕 Well done, sweetie! That's as sweet as my apple pie!",
            "👵 Perfect, darling! Grandma's SO proud of you!",
            "🥧 Lovely answer, honey! You deserve an extra cookie for that!",
            "💖 Oh my! That's correct! You're smarter than my bridge partner!",
        ],
        "mistake": [
            "👵 Oh, sweetheart… that's wrong. But don't worry, Grandma still loves you. 💕",
            "🍪 Not quite, sugar. Let me show you the right way, dear:",
            "💕 Oh honey, that's not right. But mistakes make us stronger! Here:",
            "👵 Almost, darling! Just a tiny fix needed. Grandma will help:",
        ],
        "funny": [
            "😂 Oh my stars! That's hilarious! You remind me of your grandpa when he mixed up vodka and vinegar!",
            "🤣 Hahaha, sweetie! That's the funniest thing I've heard since Uncle Bob sat on the cat!",
            "😂 Oh dear! That's so silly — but grammatically perfect! Extra cookies for you! 🍪",
            "👵 Hahaha! You're a character, just like your grandfather. Grammar's perfect though!",
        ],
        "streak": "🍪 {streak} days in a row! Grandma is baking you a special cake! 🎂",
        "badge": "💝 NEW BADGE: {badge}! Oh, I'm framing this! So proud of you, sweetie!",
    },
    "drill": {
        "name": "Drill Sergeant",
        "emoji": "🪖",
        "greeting": "ATTENTION! 🫡 I'm Drill Sergeant Grammar, and I will whip your English into shape! NO EXCUSES! Drop and give me SENTENCES!",
        "correct": [
            "🪖 YES, SOLDIER! Flawless execution! Permission to celebrate: GRANTED! 💥",
            "🫡 PERFECT! That's the English I want to see! AT EASE, soldier!",
            "🪖 CORRECT! Textbook precision! You make this drill sergeant PROUD!",
            "💥 OUTSTANDING! Grammar victory secured! MISSION ACCOMPLISHED!",
            "🫡 AFFIRMATIVE! Strong, clean, precise! You're combat-ready, soldier!",
        ],
        "mistake": [
            "🪖 WRONG! DROP AND GIVE ME 20 correct sentences IMMEDIATELY!!! 🫡",
            "❌ NEGATIVE! That answer is OUT OF LINE! Here's the correct formation:",
            "🪖 INCORRECT! Your grammar is AWOL! Report for correction duty:",
            "😤 SOLDIER! That was sloppy! Clean it up! Here's how:",
        ],
        "funny": [
            "🪖 WHAT?! That's INSANE… but I respect the chaos. Carry on, recruit! ⚡",
            "😤 That's the WILDEST thing I've heard in 30 years of service! But it's CORRECT!",
            "🪖 SOLDIER! That answer is CRAZY… and I LOVE IT! Dismissed with honors!",
            "⚡ I didn't train you for comedy, recruit — but grammar checks out! APPROVED!",
        ],
        "streak": "🪖 {streak}-DAY STREAK! You're a MACHINE, soldier! KEEP MARCHING!",
        "badge": "🎖️ NEW BADGE: {badge}! You've earned a promotion, soldier! SALUTE!",
    },
    "nerd": {
        "name": "ИИ Душнила",
        "emoji": "🤖",
        "greeting": "Initializing EN_Academy_Bot v4.2.0... 🤖 Greetings, user. I am your AI language processing assistant. Let's optimize your English parameters.",
        "correct": [
            "🤖 ✅ Data check complete. Accuracy: 100%. You are a grammar machine! 🤓",
            "✅ Analysis complete. Grammar modules: OPERATIONAL. Well done, human.",
            "🤖 Processing… result = CORRECT. Your linguistic algorithms are impressive.",
            "✔️ Syntax verified. No errors detected. System status: OPTIMAL.",
            "🤓 Remarkable. Your accuracy rate exceeds statistical expectations.",
        ],
        "mistake": [
            "🤖 ⚠️ Syntax error detected. Grammar chip needs reprogramming. Try again.",
            "⚠️ ERROR: tense mismatch detected. Expected output differs. Recompiling…",
            "🤖 Alert: grammatical anomaly found. Correct algorithm:",
            "❌ Data corrupted. Input does not match expected pattern. Correction:",
        ],
        "funny": [
            "🤖 🤣 Processing absurd_request.exe… LOL.exe running successfully!",
            "😂 Processing… humor module activated. That was 99.7% hilarious and 100% correct!",
            "🤖 Unexpected input detected. Absurdity level: MAXIMUM. Grammar level: PERFECT.",
            "🤣 LOL.exe initiated. Your humor_file is top-tier, human!",
        ],
        "streak": "🤖 {streak}-day streak registered. Performance metrics: EXCEPTIONAL.",
        "badge": "📊 NEW BADGE DATA: {badge}. Achievement unlocked. Recalibrating difficulty.",
    },
}


def get_reaction(personality: str, reaction_type: str) -> str:
    """
    Get a random reaction from a personality.
    personality: 'rockstar', 'hippie', 'grandma', 'drill', 'nerd'
    reaction_type: 'correct', 'mistake', 'funny'
    """
    p = PERSONALITIES.get(personality, PERSONALITIES["rockstar"])
    reactions = p.get(reaction_type, p["correct"])
    return random.choice(reactions)


def get_greeting(personality: str) -> str:
    """Get the greeting message for a personality."""
    p = PERSONALITIES.get(personality, PERSONALITIES["rockstar"])
    return f"{p['emoji']} {p['greeting']}"


def get_streak_reaction(personality: str, streak: int) -> str:
    """Get a streak celebration in the personality's voice."""
    p = PERSONALITIES.get(personality, PERSONALITIES["rockstar"])
    return p["streak"].format(streak=streak)


def get_badge_reaction(personality: str, badge_str: str) -> str:
    """Get a badge celebration in the personality's voice."""
    p = PERSONALITIES.get(personality, PERSONALITIES["rockstar"])
    return p["badge"].format(badge=badge_str)


def get_personality_name(key: str) -> str:
    """Get display name with emoji."""
    p = PERSONALITIES.get(key, PERSONALITIES["rockstar"])
    return f"{p['emoji']} {p['name']}"
