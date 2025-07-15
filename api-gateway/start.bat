@echo off
REM EduNerve API Gateway - Windows Start Script

echo 🌐 Starting EduNerve API Gateway...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Redis is available
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Redis is not available. Please start Redis server first.
    echo   Download Redis from: https://redis.io/download
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist .env (
    echo 📄 Creating .env file from template...
    copy .env.example .env
    echo ✅ .env file created. Please configure it with your settings.
)

REM Start the API Gateway
echo 🚀 Starting API Gateway server...
python main.py

pause
