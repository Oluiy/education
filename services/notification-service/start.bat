@echo off
echo Starting EduNerve Notification Service...
echo =====================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set environment variables
set PYTHONPATH=%CD%
set PORT=8006

REM Start the service
echo Starting service on port %PORT%...
echo Service will be available at http://localhost:%PORT%
echo API documentation at http://localhost:%PORT%/docs
echo.
echo Press Ctrl+C to stop the service
echo.

cd app
python -m uvicorn main:app --host 0.0.0.0 --port %PORT% --reload

pause
