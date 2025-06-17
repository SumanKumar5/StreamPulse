from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from api import tweets, websocket
from alerts import check_for_alerts
from logger import logger  


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routers
app.include_router(tweets.router)
app.include_router(websocket.router)

@app.get("/")
def root():
    logger.info("Health check hit at '/' route")
    return {"message": "Real-Time Sentiment API is running 🚀"}

@app.on_event("startup")
async def start_background_tasks():
    logger.info("Starting background task: alert_worker()")
    asyncio.create_task(alert_worker())

async def alert_worker():
    logger.info("Alert worker loop started")
    while True:
        try:
            check_for_alerts()
        except Exception as e:
            logger.exception("Error inside alert_worker loop")
        await asyncio.sleep(60)
