@echo off
setlocal EnableDelayedExpansion

:: Savage Leo Setup Script with Telegram Alert (Safe Version)
:: ===========================================================

:: === USER CONFIG ===
set TELEGRAM_TOKEN=8185747205:AAEDj8utKlBOcRYAMIaRqynKNxLZ3xpG8tk
set TELEGRAM_CHAT_ID=8026386062

echo [🔍] Checking if Python 3.11 is installed...
if not exist "C:\Program Files\Python311\python.exe" (
    echo [⬇️] Downloading Python 3.11.9...
    curl -L -o python-3.11.9-amd64.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

    echo [⚙️] Installing Python 3.11.9...
    start /wait python-3.11.9-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
)

set "PYTHON311=C:\Users\PC\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Python 3.11\python.exe"
if not exist "%PYTHON311%" (
    echo ❌ Python 3.11 install failed.
    exit /b 1
)

cd /d %~dp0
echo [🐍] Creating virtual environment: venv311...
"%PYTHON311%" -m venv venv311

echo [🚀] Activating venv311...
call venv311\Scripts\activate.bat

echo [📦] Installing pip packages...
pip install --upgrade pip

if exist requirements.txt (
    pip install -r requirements.txt
) else (
    pip install requests python-dotenv
)

echo [🧠] Running LLM auto fixer...
python auto_fix.py

:: === SEND TELEGRAM ALERT ===
echo [📡] Notifying Telegram...

set "TG_URL=https://api.telegram.org/bot%TELEGRAM_TOKEN%/sendMessage"
curl -s -X POST "%TG_URL%" -d "chat_id=%TELEGRAM_CHAT_ID%" -d "text=✅ Savage Leo setup complete on %COMPUTERNAME%. Ready to run. 🔥" -d "parse_mode=Markdown" >nul

echo.
echo ✅ Setup finished. Telegram alert sent.
pause
