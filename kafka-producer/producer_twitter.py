import os
import time
import json
import sys
import subprocess
from kafka import KafkaProducer
from dotenv import load_dotenv
import tweepy
from loguru import logger

# Load environment variables
load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
KAFKA_BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")

client = tweepy.Client(bearer_token=BEARER_TOKEN)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

QUERY = "Tesla lang:en -is:retweet"
MAX_RESULTS = 10
POLL_INTERVAL = 15

logger.info("🔁 Starting tweet polling...")

since_id = None

while True:
    try:
        response = client.search_recent_tweets(
            query=QUERY,
            max_results=MAX_RESULTS,
            tweet_fields=["id", "text", "created_at", "author_id"],
            since_id=since_id
        )

        tweets = response.data or []

        if tweets:
            since_id = tweets[0].id

        for tweet in reversed(tweets):
            data = {
                "id": tweet.id,
                "text": tweet.text,
                "timestamp": str(tweet.created_at),
                "author_id": tweet.author_id
            }
            logger.info(f"➡️  {data['text'][:60]}...")
            producer.send(KAFKA_TOPIC, value=data)

        time.sleep(POLL_INTERVAL)

    except tweepy.TooManyRequests:
        logger.warning("⛔ Twitter rate limit exceeded. Switching to fake_producer...")
        subprocess.run([sys.executable, "fake_producer.py"])
        break  # Exit the loop so fake takes over

    except Exception as e:
        logger.error(f"⚠️ Error while polling tweets: {e}")
        time.sleep(30)
