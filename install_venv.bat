@echo off
REM === Check Python version ===
python --version

REM === Ensure Python 3.11 is installed ===
where python311 >nul 2>nul
IF ERRORLEVEL 1 (
    echo.
    echo ❌ Python 3.11 not found.
    echo ➤ Download from: https://www.python.org/downloads/release/python-3118/
    pause
    exit /b
)

REM === Create fresh virtual environment ===
python311 -m venv venv311
call venv311\Scripts\activate

REM === Install required packages ===
pip install --upgrade pip
pip install streamlit requests python-dotenv

REM === Launch GUI Dashboard ===
streamlit run dashboard\gui_dashboard.py
