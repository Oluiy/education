@echo off
echo Starting EduNerve Assistant Service...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file with required configuration
    echo See README.md for details
    pause
)

REM Create audio directory if it doesn't exist
if not exist "audio_files\" (
    mkdir audio_files
    echo Created audio_files directory
)

REM Start the service
echo Starting Assistant Service on port 8003...
echo Press Ctrl+C to stop the service
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

pause
