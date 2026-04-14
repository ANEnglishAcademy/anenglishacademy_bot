import pytest
from database.db import create_user, get_user, update_user, increment_progress
from handlers.learning import get_task_data
from utils.helpers import evaluate_answer, translate_word

@pytest.mark.asyncio
async def test_user_creation():
    user = await create_user(12345, "TestUser")
    assert user is not None
    assert user["user_id"] == 12345
    assert user["nickname"] == "TestUser"
    assert user["level"] == ""  # Default empty

@pytest.mark.asyncio
async def test_get_task_data():
    # Setup user
    await create_user(111, "TaskUser")
    await update_user(111, level="A1", current_week=1, current_day=1, onboarding_complete=1)
    
    user = await get_user(111)
    task_data, level, week, day = await get_task_data(user)
    
    assert level == "A1"
    assert week == 1
    assert day == 1
    assert task_data is not None
    assert "topic" in task_data
    assert "Present Simple" in task_data["topic"]

@pytest.mark.asyncio
async def test_evaluate_answer():
    keywords = ["apple", "banana"]
    
    # Correct
    assert evaluate_answer("I like apple", keywords) == "correct"
    assert evaluate_answer("Banana is good", keywords) == "correct"
    
    # Mistake
    assert evaluate_answer("I like pear", keywords) == "mistake"
    
    # Funny/Flair (might be random, so we test deterministically or checking logic)
    # The helper says >40 chars or emoji might be funny.
    # We can just check it returns a valid string.
    res = evaluate_answer("Meaning of life is 42", [])
    assert res in ["mistake", "funny", "correct"]

@pytest.mark.asyncio
async def test_translation_local():
    assert translate_word("weird") == "странный, необычный"
    assert translate_word("Weird ") == "странный, необычный"  # Case/trim check
    assert translate_word("unknownword123") is None

@pytest.mark.asyncio
async def test_progress_increment():
    await create_user(222, "ProgressUser")
    await update_user(222, tasks_completed=0, current_day=1, current_week=1)
    
    # +1 Task
    res = await increment_progress(222)
    
    assert res["tasks_completed"] == 1
    assert res["current_day"] == 2  # Advanced to day 2
    assert res["streak_days"] == 1  # First day streak
    
    # Check looping logic (Week 1 Day 7 -> Week 2 Day 1)
    await update_user(222, current_day=7, current_week=1)
    res = await increment_progress(222)
    assert res["current_day"] == 1
    assert res["current_week"] == 2
