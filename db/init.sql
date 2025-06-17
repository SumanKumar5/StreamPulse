-- Drop existing objects (for dev purposes)
DROP MATERIALIZED VIEW IF EXISTS sentiment_minute;
DROP TABLE IF EXISTS tweets CASCADE;

-- Main tweets table
CREATE TABLE tweets (
  tweet_id TEXT,
  timestamp TIMESTAMPTZ NOT NULL,
  keyword TEXT,
  text TEXT,
  sentiment TEXT,
  score FLOAT,
  UNIQUE(tweet_id, timestamp)  -- Required for hypertable
);

-- Convert to hypertable
SELECT create_hypertable('tweets', 'timestamp', if_not_exists => TRUE);

-- Continuous aggregate: per-minute sentiment summary
CREATE MATERIALIZED VIEW sentiment_minute
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 minute', timestamp) AS minute,
  keyword,
  AVG(
    CASE sentiment
      WHEN 'positive' THEN 1
      WHEN 'negative' THEN -1
      ELSE 0
    END
  ) AS avg_score,
  COUNT(*) FILTER (WHERE sentiment = 'positive') AS pos_count,
  COUNT(*) FILTER (WHERE sentiment = 'negative') AS neg_count,
  COUNT(*) FILTER (WHERE sentiment = 'neutral')  AS neu_count
FROM tweets
GROUP BY 1, 2;

-- Indexes for performance
CREATE INDEX idx_sentiment ON tweets(sentiment);
CREATE INDEX idx_keyword ON tweets(keyword);

-- ✅ Enable compression (legacy-compatible)
ALTER TABLE tweets SET (
    timescaledb.compress = true,
    timescaledb.compress_segmentby = 'keyword, tweet_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- ✅ Add compression policy
SELECT add_compression_policy('tweets', INTERVAL '7 days');

