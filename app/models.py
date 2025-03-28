from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaoDividends(BaseModel):
    netuid: int
    hotkey: str
    dividends: float
    timestamp: datetime
    cached: bool = False


class SentimentAnalysis(BaseModel):
    netuid: int
    hotkey: str
    sentiment_score: float
    tweet_count: int
    timestamp: datetime
    action_taken: Optional[str] = None  # 'stake' or 'unstake'
    action_amount: Optional[float] = None
