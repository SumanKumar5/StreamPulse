from pydantic import BaseModel
from datetime import datetime

class Tweet(BaseModel):
    tweet_id: str
    timestamp: datetime
    keyword: str
    text: str
    sentiment: str
    score: float

class SentimentBucket(BaseModel):
    minute: datetime
    keyword: str
    avg_score: float
    pos_count: int
    neg_count: int
    neu_count: int
