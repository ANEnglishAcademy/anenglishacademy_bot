# AN English Academy Bot 🤖

This is the **English-only MVP** version of the Telegram learning bot for **AN English Academy**.  
It provides daily English practice, progress tracking, grammar tips (in Russian), and a fun, gamified experience.

---

## 📌 Features

### 👋 Onboarding
- `/start` → Welcome message, optional nickname setup
- `/help` → List of available commands
- `/setlevel` → Choose English level (A1–C1)
- `/setnickname` → Set your display nickname
- `/mynickname` → Show/change nickname (inline edit)

---

### 📚 Learning & Tasks
- `/task` → Get today’s rotating daily task
- `/nexttask` → Preview tomorrow’s task
- `/previoustask` → Review yesterday’s task
- `/answer your_text` → Submit your answer and receive quick feedback
- `/grammar` → Random grammar explanation in **Russian only**

---

### 📊 Progress & Motivation
- `/profile` → View your stats:
  - Nickname
  - Level
  - Tasks completed
  - Progress bar (towards next badge)
  - Badge system 🌱🥉🥈🥇🏆
  - Current streak 🔥
  - Record streak 🏅
  - Joined date 📅
  - Last reset 🕒
  - Motivation message 💡

- `/resetprogress` → Reset your progress (with confirmation buttons)

- Milestones 🎉:
  - 10 tasks → 🥈 Rising Star
  - 20 tasks → 🥇 Pro
  - 50 tasks → 🏆 Legend

- Streak milestones 🎊:
  - 3 days → 🔥 3-day streak
  - 7 days → ⚡ 7-day streak
  - 14 days → 🌟 2 weeks
  - 30 days → 🏅 1 month

---

### 🏆 Leaderboard
- `/top` → Shows the top learners ranked by **tasks completed**
- Leaderboard displays nicknames if set, otherwise `User {id}`

---

## 📂 File Structure

