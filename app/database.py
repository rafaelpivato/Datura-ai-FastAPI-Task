import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis

from app.models import SentimentAnalysis, TaoDividends

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tao_dividends")

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = int(os.getenv("CACHE_TTL", "120"))  # 2 minutes in seconds

# MongoDB client
mongo_client: Optional[AsyncIOMotorClient] = None

# Redis client
redis_client: Optional[aioredis.Redis] = None


async def init_db():
    global mongo_client
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    return mongo_client[DATABASE_NAME]


async def init_redis():
    global redis_client
    redis_client = await aioredis.from_url(
        REDIS_URL, encoding="utf-8", decode_responses=True
    )
    return redis_client


async def get_cached_dividends(netuid: int, hotkey: str) -> Optional[TaoDividends]:
    if not redis_client:
        return None

    cache_key = f"dividends:{netuid}:{hotkey}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        dividends = TaoDividends.parse_raw(cached_data)
        dividends.cached = True
        return dividends
    return None


async def cache_dividends(dividends: TaoDividends):
    if not redis_client:
        return

    cache_key = f"dividends:{dividends.netuid}:{dividends.hotkey}"
    await redis_client.set(cache_key, dividends.json(), ex=CACHE_TTL)


async def store_dividends(dividends: TaoDividends):
    if not mongo_client:
        return

    collection = mongo_client[DATABASE_NAME]["dividends"]
    await collection.insert_one(dividends.dict())


async def store_sentiment(sentiment: SentimentAnalysis):
    if not mongo_client:
        return

    collection = mongo_client[DATABASE_NAME]["sentiment"]
    await collection.insert_one(sentiment.dict())
