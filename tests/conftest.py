import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis

from app.main import app
from app.database import init_db, init_redis

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
async def test_db():
    # Use a separate test database
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    test_db = client["test_tao_dividends"]
    yield test_db
    # Cleanup after tests
    await client.drop_database("test_tao_dividends")

@pytest.fixture
async def test_redis():
    # Use a separate Redis database for testing
    redis = await aioredis.from_url(
        "redis://localhost:6379/1",
        encoding="utf-8",
        decode_responses=True
    )
    yield redis
    # Cleanup after tests
    await redis.flushdb()
    await redis.close()

@pytest.fixture
def test_token():
    # Return a test token for authenticated endpoints
    return "test_token"