@echo off
echo Starting EduNerve File Storage Service...
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
echo Starting File Storage Service on http://localhost:8005...
echo.
echo Press Ctrl+C to stop the service
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
