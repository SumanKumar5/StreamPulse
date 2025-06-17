from db import get_db_connection
from email_utils import send_email
from datetime import datetime, timedelta

last_alert_times = {}

ALERT_THRESHOLD = -0.5
COOLDOWN_MINUTES = 10

def check_for_alerts():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT keyword, AVG(avg_score), SUM(pos_count), SUM(neg_count), SUM(neu_count)
        FROM sentiment_minute
        WHERE minute > NOW() - INTERVAL '5 minutes'
        GROUP BY keyword;
    """)

    rows = cur.fetchall()
    conn.close()

    for row in rows:
        keyword, avg_score, pos, neg, neu = row

        if avg_score < ALERT_THRESHOLD and neg > pos:
            last_alert = last_alert_times.get(keyword)
            now = datetime.utcnow()

            if not last_alert or (now - last_alert).total_seconds() > COOLDOWN_MINUTES * 60:
                subject = f"🚨 Alert: Negative Sentiment Surge for {keyword}"
                body = (
                    f"⚠️ Keyword: {keyword}\n\n"
                    f"Average Sentiment Score (5m): {avg_score:.2f}\n"
                    f"Positive: {pos}, Negative: {neg}, Neutral: {neu}"
                )

                send_email(subject, body)
                last_alert_times[keyword] = now
