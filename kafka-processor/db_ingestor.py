import json
import psycopg2
from kafka import KafkaConsumer
from datetime import datetime

# Kafka setup
KAFKA_TOPIC = "tweets_processed"
KAFKA_BOOTSTRAP_SERVER = "localhost:9093"

# PostgreSQL setup
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB = "sentiment_db"
PG_USER = "postgres"
PG_PASSWORD = "postgres"

# Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset='earliest',
    group_id="db-ingestor"
)

# PostgreSQL connection
conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASSWORD
)
cursor = conn.cursor()

print("🗃️ DB Ingestor started...")

for message in consumer:
    tweet = message.value

    try:
        # Basic validation
        tweet_id = tweet["tweet_id"]
        timestamp = tweet["timestamp"]
        keyword = tweet["keyword"]
        text = tweet["text"]
        sentiment = tweet["sentiment"]
        score = tweet["score"]

        # Insert into DB
        cursor.execute("""
            INSERT INTO tweets (tweet_id, timestamp, keyword, text, sentiment, score)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (tweet_id, timestamp, keyword, text, sentiment, score))

        conn.commit()
        print(f"✅ Inserted: {text[:60]}... ({sentiment})")

    except Exception as e:
        print(f"⚠️ Error inserting tweet: {e}")
        conn.rollback()
