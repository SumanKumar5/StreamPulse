@echo off
setlocal

echo Starting Docker containers...
docker compose up -d

echo Waiting 10 seconds for containers to initialize...
timeout /T 10 /NOBREAK > NUL

REM --- Start the Kafka Producer ---
echo Starting Kafka Producer...
cd kafka-producer
call venv\Scripts\activate
start cmd /c "python producer_twitter.py"

cd ..

REM --- Start Sentiment Processor ---
echo Starting Sentiment Processor...
cd kafka-processor
call venv\Scripts\activate
start cmd /c "python processor_sentiment.py"

REM --- Start DB Ingestor ---
echo Starting DB Ingestor...
start cmd /c "python db_ingestor.py"

cd ..

REM --- Start FastAPI App (Sentiment API) ---
echo Starting FastAPI Backend...
cd backend
call venv\Scripts\activate
start cmd /c "uvicorn main:app --reload"

echo All services started!
pause
