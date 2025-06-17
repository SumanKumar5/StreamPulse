from loguru import logger
import os

# Write logs to file 
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger.add(
    os.path.join(LOG_DIR, "pipeline.log"),
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    enqueue=True,
    backtrace=True,
    diagnose=True
)
