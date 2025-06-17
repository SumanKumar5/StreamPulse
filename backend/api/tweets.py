from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta
from db import get_db_connection
from models import Tweet, SentimentBucket

router = APIRouter()

@router.get("/sentiment-counts")
def fetch_sentiment_counts(keyword: str = Query(...)):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE sentiment = 'positive') AS pos_count,
            COUNT(*) FILTER (WHERE sentiment = 'negative') AS neg_count,
            COUNT(*) FILTER (WHERE sentiment = 'neutral')  AS neu_count
        FROM tweets
        WHERE keyword = %s
    """, (keyword,))
    
    result = cur.fetchone()
    conn.close()
    
    return {
        "positive": result[0],
        "negative": result[1],
        "neutral": result[2]
    }


@router.get("/tweets/latest", response_model=List[Tweet])
def get_latest_tweets(
    limit: int = Query(20, le=100),
    keyword: Optional[str] = None,
    page: int = 1
):
    offset = (page - 1) * limit
    conn = get_db_connection()
    cur = conn.cursor()

    if keyword:
        cur.execute(
            """
            SELECT tweet_id, timestamp, keyword, text, sentiment, score
            FROM tweets
            WHERE keyword = %s
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
            """,
            (keyword, limit, offset)
        )
    else:
        cur.execute(
            """
            SELECT tweet_id, timestamp, keyword, text, sentiment, score
            FROM tweets
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )

    rows = cur.fetchall()
    conn.close()

    return [Tweet(
        tweet_id=row[0],
        timestamp=row[1],
        keyword=row[2],
        text=row[3],
        sentiment=row[4],
        score=row[5]
    ) for row in rows]

@router.get("/sentiment-trend", response_model=List[SentimentBucket])
def get_sentiment_trend(
    minutes: int = 60,
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None
):
    conn = get_db_connection()
    cur = conn.cursor()

    if from_time and to_time:
        cur.execute(
            """
            SELECT minute, keyword, avg_score, pos_count, neg_count, neu_count
            FROM sentiment_minute
            WHERE minute BETWEEN %s AND %s
            ORDER BY minute ASC
            """,
            (from_time, to_time)
        )
    else:
        cur.execute(
            """
            SELECT minute, keyword, avg_score, pos_count, neg_count, neu_count
            FROM sentiment_minute
            WHERE minute > now() - interval %s
            ORDER BY minute ASC
            """,
            (f"{minutes} minutes",)
        )

    rows = cur.fetchall()
    conn.close()

    return [SentimentBucket(
        minute=row[0],
        keyword=row[1],
        avg_score=row[2],
        pos_count=row[3],
        neg_count=row[4],
        neu_count=row[5]
    ) for row in rows]

@router.get("/summary")
def get_summary():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM tweets")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tweets WHERE sentiment = 'positive'")
    pos = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tweets WHERE sentiment = 'negative'")
    neg = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tweets WHERE sentiment = 'neutral'")
    neu = cur.fetchone()[0]

    cur.execute("SELECT AVG(score) FROM tweets")
    avg = cur.fetchone()[0]

    conn.close()
    return {
        "total_tweets": total,
        "positive": pos,
        "negative": neg,
        "neutral": neu,
        "avg_score": round(avg or 0, 4)
    }
