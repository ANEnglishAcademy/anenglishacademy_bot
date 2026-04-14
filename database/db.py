"""
SQLite async database layer for AN English Academy Bot.
Stores user profiles, progress, streaks, and settings.
"""

import aiosqlite
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bot_data.db")


async def init_db():
    """Create tables if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                nickname TEXT DEFAULT '',
                level TEXT DEFAULT '',
                personality TEXT DEFAULT '',
                language_mode TEXT DEFAULT 'bilingual',
                focus TEXT DEFAULT '',
                frequency TEXT DEFAULT 'daily',
                duration TEXT DEFAULT 'coffee',
                current_week INTEGER DEFAULT 1,
                current_day INTEGER DEFAULT 1,
                tasks_completed INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                last_active TEXT DEFAULT '',
                joined_at TEXT DEFAULT '',
                onboarding_complete INTEGER DEFAULT 0,
                awaiting_answer INTEGER DEFAULT 0,
                referred_by INTEGER DEFAULT NULL,
                referrals_count INTEGER DEFAULT 0
            )
        """)
        
        # Migrations for existing DB
        try:
            await db.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER DEFAULT NULL")
        except aiosqlite.OperationalError:
            pass  # Column already exists
            
        try:
            await db.execute("ALTER TABLE users ADD COLUMN referrals_count INTEGER DEFAULT 0")
        except aiosqlite.OperationalError:
            pass  # Column already exists
            
        await db.commit()


async def get_user(user_id: int) -> dict | None:
    """Get a user's data by Telegram user ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None


async def create_user(user_id: int, nickname: str = "") -> dict:
    """Create a new user record."""
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users (user_id, nickname, joined_at, last_active)
               VALUES (?, ?, ?, ?)""",
            (user_id, nickname, now, now),
        )
        await db.commit()
    return await get_user(user_id)


async def update_user(user_id: int, **kwargs):
    """Update user fields. Pass field=value pairs."""
    if not kwargs:
        return
    set_clause = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = ?", values
        )
        await db.commit()


async def increment_progress(user_id: int):
    """Increment tasks_completed, advance day/week, and update streak."""
    user = await get_user(user_id)
    if not user:
        return

    tasks = user["tasks_completed"] + 1
    day = user["current_day"] + 1
    week = user["current_week"]

    if day > 7:
        day = 1
        week += 1
        if week > 4:
            week = 1  # Loop back to week 1

    # Streak logic
    today_str = date.today().isoformat()
    last_active = user["last_active"][:10] if user["last_active"] else ""
    streak = user["streak_days"]
    best = user["best_streak"]

    if last_active == today_str:
        # Already active today — don't double-count streak
        pass
    elif last_active == date.today().strftime("%Y-%m-%d"):
        pass
    else:
        # Check if yesterday
        from datetime import timedelta
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        if last_active == yesterday:
            streak += 1
        else:
            streak = 1  # Reset streak

    if streak > best:
        best = streak

    await update_user(
        user_id,
        tasks_completed=tasks,
        current_day=day,
        current_week=week,
        streak_days=streak,
        best_streak=best,
        last_active=datetime.now().isoformat(),
        awaiting_answer=0,
    )

    return {
        "tasks_completed": tasks,
        "streak_days": streak,
        "best_streak": best,
        "current_day": day,
        "current_week": week,
    }


async def get_top_users(limit: int = 10) -> list:
    """Get leaderboard: top users by tasks_completed."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE onboarding_complete = 1 ORDER BY tasks_completed DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def reset_progress(user_id: int):
    """Reset a user's progress (keep settings)."""
    await update_user(
        user_id,
        current_week=1,
        current_day=1,
        tasks_completed=0,
        streak_days=0,
        best_streak=0,
        last_active=datetime.now().isoformat(),
        awaiting_answer=0,
    )

async def add_referral(new_user_id: int, referrer_id: int):
    """Link a new user to a referrer and increment referrer's count."""
    referrer = await get_user(referrer_id)
    if not referrer:
        return False
        
    async with aiosqlite.connect(DB_PATH) as db:
        # Update new user
        await db.execute(
            "UPDATE users SET referred_by = ? WHERE user_id = ?",
            (referrer_id, new_user_id)
        )
        # Update referrer
        await db.execute(
            "UPDATE users SET referrals_count = referrals_count + 1 WHERE user_id = ?",
            (referrer_id,)
        )
        await db.commit()
    return True
