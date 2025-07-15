@echo off
echo Starting EduNerve Sync & Messaging Service...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set environment variables
set PYTHONPATH=%CD%

REM Start the service
echo Starting Sync & Messaging Service on http://localhost:8004...
echo WebSocket available at ws://localhost:8004/ws
echo.
echo Press Ctrl+C to stop the service
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
