import unittest
import asyncio
import os
import sys
import shutil
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions to test
try:
    from database.db import create_user, get_user, update_user, increment_progress, init_db
    from handlers.learning import get_task_data
    from utils.helpers import evaluate_answer, translate_word
except ImportError as e:
    print(f"Import Error: {e}")
    exit(1)

TEST_DB = "verify_bot.db"

class TestBotLogic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Patch DB path
        self.patcher = patch("database.db.DB_PATH", TEST_DB)
        self.mock_db_path = self.patcher.start()
        
        # Init DB
        await init_db()

    async def asyncTearDown(self):
        self.patcher.stop()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    async def test_user_creation(self):
        print("Testing User Creation...")
        user = await create_user(12345, "TestUser")
        self.assertIsNotNone(user)
        self.assertEqual(user["user_id"], 12345)
        self.assertEqual(user["nickname"], "TestUser")
        
    async def test_get_task_data(self):
        print("Testing Task Data Retrieval...")
        await create_user(111, "TaskUser")
        await update_user(111, level="A1", current_week=1, current_day=1, onboarding_complete=1)
        
        user = await get_user(111)
        task_data, level, week, day = await get_task_data(user)
        
        self.assertEqual(level, "A1")
        self.assertEqual(week, 1)
        self.assertIsNotNone(task_data)
        self.assertIn("topic", task_data)
        
    async def test_evaluate_answer(self):
        print("Testing Answer Evaluation...")
        keywords = ["apple", "banana"]
        self.assertEqual(evaluate_answer("I like apple", keywords), "correct")
        self.assertEqual(evaluate_answer("Wrong fruit", keywords), "mistake")
        
    async def test_translation(self):
        print("Testing Translation...")
        self.assertEqual(translate_word("weird"), "странный, необычный")
        
    async def test_progress(self):
        print("Testing Progress Increment...")
        await create_user(222, "ProgressUser")
        # Ensure fresh state
        await update_user(222, tasks_completed=0, current_day=1, current_week=1, streak_days=0)
        
        res = await increment_progress(222)
        self.assertEqual(res["tasks_completed"], 1)
        self.assertEqual(res["current_day"], 2)

if __name__ == "__main__":
    unittest.main()
