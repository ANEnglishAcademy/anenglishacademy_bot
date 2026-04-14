import pytest
import os
import asyncio
from database.db import init_db

TEST_DB = "test_bot.db"



@pytest.fixture(autouse=True)
async def setup_db(monkeypatch):
    """Setup a temporary test database for each test."""
    # Patch the DB_PATH in database.db module
    monkeypatch.setattr("database.db.DB_PATH", TEST_DB)
    
    # Initialize the database (create tables)
    await init_db()
    
    yield
    
    # Teardown: Remove the test database file
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
