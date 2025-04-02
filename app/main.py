import logging
import os
from datetime import datetime

from celery import Celery
from dotenv import load_dotenv
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

# Load environment variables
load_dotenv()

# Configure logging based on DEBUG environment variable
debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "t")
log_level = logging.DEBUG if debug_mode else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery("app", broker="redis://localhost:6379/0")

app = FastAPI(
    title="Tao Dividends API",
    description="Asynchronous FastAPI service for querying Tao dividends from the Bittensor blockchain",
    version="0.1.0",
    debug=debug_mode,
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
    logger.info(
        "Starting Tao Dividends API in %s mode",
        "debug" if debug_mode else "production",
    )
    await init_db()
    await init_redis()


@app.get("/")
async def root():
    logger.debug("Root endpoint accessed")
    return {"message": "Welcome to Tao Dividends API"}


@app.get("/api/v1/tao_dividends")
async def get_tao_dividends(
    netuid: int,
    hotkey: str,
    trade: bool = False,
    token: str = Depends(oauth2_scheme),
):
    # TODO: IMPLEMENT AUTHENTICATION AND AUTHORIZATION
    logger.debug(
        "Tao dividends requested for netuid=%s, hotkey=%s, trade=%s",
        netuid,
        hotkey,
        trade,
    )

    # First check cache
    cached_result = await get_cached_dividends(netuid, hotkey)
    if cached_result:
        logger.debug("Cache hit for netuid=%s, hotkey=%s", netuid, hotkey)
        return cached_result

    logger.debug(
        "Cache miss for netuid=%s, hotkey=%s, querying blockchain",
        netuid,
        hotkey,
    )

    # Query blockchain
    querier = TaoDividendQuerier()
    try:
        logger.debug(
            "Querying blockchain for dividends: netuid=%s, hotkey=%s",
            netuid,
            hotkey,
        )
        dividend_balance = await querier.get_tao_dividends_per_subnet(netuid, hotkey)
        if dividend_balance is None:
            logger.debug(
                "No dividend data found for netuid=%s, hotkey=%s",
                netuid,
                hotkey,
            )
            return {"error": "No dividend data found"}

        logger.debug(
            "Dividend balance retrieved: %s for netuid=%s, hotkey=%s",
            dividend_balance,
            netuid,
            hotkey,
        )

        # Create response model
        dividends = TaoDividends(
            netuid=netuid,
            hotkey=hotkey,
            dividends=float(dividend_balance),
            timestamp=datetime.utcnow(),
        )

        # Cache and store results
        logger.debug(
            "Caching and storing dividend results for netuid=%s, hotkey=%s",
            netuid,
            hotkey,
        )
        await cache_dividends(dividends)
        await store_dividends(dividends)

        # If trade flag is set, trigger sentiment analysis
        if trade:
            logger.debug(
                "Trade flag set, triggering sentiment analysis for netuid=%s, hotkey=%s",
                netuid,
                hotkey,
            )
            await celery_app.send_task(
                "app.worker.analyze_sentiment",
                args=[netuid, hotkey],
            )

        return dividends
    finally:
        await querier.close()
