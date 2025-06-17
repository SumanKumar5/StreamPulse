
import time
import json
from kafka import KafkaProducer
from dotenv import load_dotenv
from loguru import logger
import os
from datetime import datetime
import random

load_dotenv()

KAFKA_BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

MOCK_TWEETS = [
    # Positive
    "Tesla just unveiled its stunning new model 🚗",
    "I absolutely love my Tesla Model 3!",
    "Tesla stock is booming today 📈",
    "Electric vehicles are the future, and Tesla leads the way!",
    "Thanks Elon, the latest Tesla update is amazing!",

    # Negative
    "Tesla's quality control is really going downhill 😤",
    "Another Tesla crash makes headlines again...",
    "I regret buying a Tesla, support is horrible.",
    "The autopilot failed me, very disappointed.",
    "Tesla's prices are too high for what they offer now.",

    # Neutral
    "Elon Musk is tweeting about Dogecoin again.",
    "Tesla's quarterly report is out.",
    "Just spotted a Tesla on the road.",
    "Reading about Tesla’s new battery technology.",
    "Visited a Tesla showroom today."
]


logger.info("📦 Fake Producer Started...")

while True:
    mock = {
        "id": random.randint(1000000000, 9999999999),
        "text": random.choice(MOCK_TWEETS),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "author_id": str(random.randint(1000, 9999))
    }
    logger.info(f"📤 Sending mock tweet: {mock['text']}")
    producer.send(KAFKA_TOPIC, value=mock)
    time.sleep(5)
