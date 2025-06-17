@echo off
setlocal enabledelayedexpansion

echo Stopping all StreamPulse services...

REM === Kill Python scripts using WMIC for reliability ===
echo Looking for running Python/Uvicorn processes...

REM --- Kill the Producer (and its potential fallback) ---

REM 1. Find producer_twitter.py and kill its ENTIRE process tree (/T)
for /f "tokens=2 delims==" %%a in ('wmic process where "name='python.exe' and commandline like '%%producer_twitter.py%%'" get processid /value ^| findstr "ProcessId"') do (
    for /f %%b in ("%%a") do (
        taskkill /T /PID %%b /F >nul
        echo   Killed producer_twitter.py process tree (PID %%b)
    )
)

REM 2. As a fallback, find and kill fake_producer.py directly
for /f "tokens=2 delims==" %%a in ('wmic process where "name='python.exe' and commandline like '%%fake_producer.py%%'" get processid /value ^| findstr "ProcessId"') do (
    for /f %%b in ("%%a") do (
        taskkill /PID %%b /F >nul
        echo   Killed fallback fake_producer.py (PID %%b)
    )
)

REM --- Kill other services ---

REM Kill processor_sentiment.py
for /f "tokens=2 delims==" %%a in ('wmic process where "name='python.exe' and commandline like '%%processor_sentiment.py%%'" get processid /value ^| findstr "ProcessId"') do (
    for /f %%b in ("%%a") do (
        taskkill /PID %%b /F >nul
        echo   Killed processor_sentiment.py (PID %%b)
    )
)

REM Kill db_ingestor.py
for /f "tokens=2 delims==" %%a in ('wmic process where "name='python.exe' and commandline like '%%db_ingestor.py%%'" get processid /value ^| findstr "ProcessId"') do (
    for /f %%b in ("%%a") do (
        taskkill /PID %%b /F >nul
        echo   Killed db_ingestor.py (PID %%b)
    )
)

REM Kill FastAPI (uvicorn)
for /f "tokens=2 delims==" %%a in ('wmic process where "name='python.exe' and commandline like '%%uvicorn%%'" get processid /value ^| findstr "ProcessId"') do (
    for /f %%b in ("%%a") do (
        taskkill /PID %%b /F >nul
        echo   Killed uvicorn (PID %%b)
    )
)

REM === Docker shutdown ===
echo.
echo Stopping Docker containers...
docker compose down

echo.
echo All services stopped.
pause