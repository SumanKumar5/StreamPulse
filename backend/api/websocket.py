from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from db import get_db_connection
from datetime import datetime, timedelta
import asyncio

router = APIRouter()

active_tweet_connections = []
active_sentiment_connections = []

@router.websocket("/ws/tweets")
async def ws_tweets(websocket: WebSocket):
    await websocket.accept()
    active_tweet_connections.append(websocket)

    try:
        last_sent = None
        while True:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT tweet_id, timestamp, keyword, text, sentiment, score
                FROM tweets
                WHERE timestamp > now() - interval '10 seconds'
                ORDER BY timestamp DESC
                LIMIT 5
            """)
            rows = cur.fetchall()
            conn.close()

            new_data = [
                {
                    "tweet_id": row[0],
                    "timestamp": row[1].isoformat(),
                    "keyword": row[2],
                    "text": row[3],
                    "sentiment": row[4],
                    "score": row[5]
                } for row in rows
            ]

            if new_data:
                await websocket.send_json(new_data)

            await asyncio.sleep(5)

    except WebSocketDisconnect:
        active_tweet_connections.remove(websocket)

@router.websocket("/ws/sentiment")
async def ws_sentiment(websocket: WebSocket):
    await websocket.accept()
    active_sentiment_connections.append(websocket)

    try:
        while True:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT minute, keyword, avg_score, pos_count, neg_count, neu_count
                FROM sentiment_minute
                WHERE minute > now() - interval '10 minutes'
                ORDER BY minute DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            conn.close()

            if row:
                await websocket.send_json({
                    "minute": row[0].isoformat(),
                    "keyword": row[1],
                    "avg_score": row[2],
                    "pos_count": row[3],
                    "neg_count": row[4],
                    "neu_count": row[5]
                })

            await asyncio.sleep(15)

    except WebSocketDisconnect:
        active_sentiment_connections.remove(websocket)
