import os
import json
from kafka import KafkaConsumer, KafkaProducer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from scipy.special import softmax
from loguru import logger

# Kafka setup
KAFKA_INPUT_TOPIC = "tweets_raw"
KAFKA_OUTPUT_TOPIC = "tweets_processed"
KAFKA_BOOTSTRAP_SERVER = "localhost:9093"

# Load tokenizer and model
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# Kafka Consumer (manual commit, batched)
consumer = KafkaConsumer(
    KAFKA_INPUT_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset='earliest',
    group_id="sentiment-processor",
    enable_auto_commit=False
)

# Kafka Producer (writes to tweets_processed)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=3  # retry up to 3 times if Kafka is busy
)

# Label mapping
LABELS = {0: "negative", 1: "neutral", 2: "positive"}

logger.info("🧠 Sentiment Processor Started...")

while True:
    # Poll for messages (wait up to 1s, max 16 at a time)
    messages_batch = consumer.poll(timeout_ms=1000, max_records=16)

    for tp, messages in messages_batch.items():
        for message in messages:
            try:
                tweet = message.value
                text = tweet.get("text", "").strip()
                if not text:
                    continue

                # Tokenize and predict
                encoded = tokenizer(text, return_tensors="pt", truncation=True)
                with torch.no_grad():
                    output = model(**encoded)
                    scores = softmax(output.logits.numpy()[0])
                    label_id = int(scores.argmax())
                    sentiment = LABELS[label_id]
                    confidence = float(scores[label_id])

                enriched = {
                    "tweet_id": tweet["id"],
                    "timestamp": tweet["timestamp"],
                    "keyword": "tesla",  # hardcoded
                    "text": tweet["text"],
                    "sentiment": sentiment,
                    "score": round(confidence, 4)
                }

                # Log and produce
                logger.info(f"[{sentiment.upper()}] {text[:60]}... ({confidence:.2f})")
                producer.send(KAFKA_OUTPUT_TOPIC, enriched)

                # Commit after successful send
                consumer.commit()

            except Exception as e:
                logger.error(f"⚠️ Error processing tweet: {e}")
