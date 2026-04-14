from aiogram.fsm.state import State, StatesGroup

class OnboardingStates(StatesGroup):
    choosing_language = State()   # Step 1: EN-only or bilingual
    choosing_level = State()      # Step 2: A1–C1
    choosing_personality = State() # Step 3: teacher vibe
    choosing_focus = State()      # Step 4: Speaking/Writing/etc.
    typing_nickname = State()     # Step 5: what to call them
