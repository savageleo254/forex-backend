@echo off
REM =============================================
REM Forex QuantOps AI System - Launch All Services
REM =============================================

REM ----------- Activate Python venv ------------
cd /d "C:\Users\PC\forex-backend"
call venv\Scripts\activate

REM ---------- 1. Start FastAPI Backend ----------
start "FastAPI Backend" cmd /k uvicorn backend_api:app --host 127.0.0.1 --port 8000

REM ---------- 2. Start News/Sentiment Feed -----
start "News Feed" cmd /k python news_feed.py

REM ---------- 3. Start Watchdog/Process Monitor -
start "Watchdog" cmd /k python watchdog.py

REM ---------- 4. (OPTIONAL) Telegram Alerts -----
REM Uncomment if you have a separate telegram_alerts.py process
REM start "Telegram Alerts" cmd /k python telegram_alerts.py

REM ---------- 5. (OPTIONAL) Dashboard ----------
REM If you have a dashboard (e.g., dashboard.py or Next.js)
REM start "Dashboard" cmd /k uvicorn dashboard:app --host 127.0.0.1 --port 8001

REM ---------- 6. (OPTIONAL) Additional Workers --
REM Add more lines for additional services as needed

echo All QuantOps services launched!
pause