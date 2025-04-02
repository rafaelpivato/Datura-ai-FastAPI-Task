from datetime import datetime

from celery import Celery
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.database import (
    cache_dividends,
    get_cached_dividends,
    init_db,
    init_redis,
    store_dividends,
)
from app.models import TaoDividends
from app.taodiv import TaoDividendQuerier

# Initialize Celery
celery_app = Celery("app", broker="redis://localhost:6379/0")

app = FastAPI(
    title="Tao Dividends API",
    description="Asynchronous FastAPI service for querying Tao dividends from the Bittensor blockchain",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.on_event("startup")
async def startup_event():
    await init_db()
    await init_redis()


@app.get("/")
async def root():
    return {"message": "Welcome to Tao Dividends API"}


@app.get("/api/v1/tao_dividends")
async def get_tao_dividends(
    netuid: int,
    hotkey: str,
    trade: bool = False,
    token: str = Depends(oauth2_scheme),
):
    # TODO: IMPLEMENT AUTHENTICATION AND AUTHORIZATION

    # First check cache
    cached_result = await get_cached_dividends(netuid, hotkey)
    if cached_result:
        return cached_result

    # Query blockchain
    querier = TaoDividendQuerier()
    try:
        dividend_balance = await querier.get_tao_dividends_per_subnet(netuid, hotkey)
        if dividend_balance is None:
            return {"error": "No dividend data found"}

        # Create response model
        dividends = TaoDividends(
            netuid=netuid,
            hotkey=hotkey,
            dividends=float(dividend_balance),
            timestamp=datetime.utcnow(),
        )

        # Cache and store results
        await cache_dividends(dividends)
        await store_dividends(dividends)

        # If trade flag is set, trigger sentiment analysis
        if trade:
            await celery_app.send_task(
                "app.worker.analyze_sentiment", args=[netuid, hotkey]
            )

        return dividends
    finally:
        await querier.close()
