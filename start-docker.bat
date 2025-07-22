@echo off
REM ==============================================================================
REM EduNerve Docker Setup and Startup Script (Windows)
REM ==============================================================================

echo 🚀 EduNerve Docker Setup ^& Startup
echo ==================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your actual configuration before running the services
    echo    Key items to configure:
    echo    - OPENAI_API_KEY=your-actual-openai-key
    echo    - WHATSAPP_API_KEY=your-actual-whatsapp-key
    echo    - TWILIO_ACCOUNT_SID=your-actual-twilio-sid
    echo    - TWILIO_AUTH_TOKEN=your-actual-twilio-token
    echo    - SMTP_USER=your-email@gmail.com
    echo    - SMTP_PASSWORD=your-email-password
    echo    - JWT_SECRET=your-production-jwt-secret
    echo.
    pause
)

echo 🔧 Preparing Docker environment...

REM Create necessary directories
if not exist uploads mkdir uploads
if not exist data\postgres mkdir data\postgres
if not exist data\redis mkdir data\redis

echo 🧹 Cleaning up previous containers (if any)...
docker-compose down -v >nul 2>&1

echo 🏗️  Building Docker images...
docker-compose build --no-cache

if errorlevel 1 (
    echo ❌ Docker build failed. Please check the error messages above.
    pause
    exit /b 1
)

echo 🚀 Starting EduNerve services...
docker-compose up -d

if errorlevel 1 (
    echo ❌ Failed to start services. Please check the error messages above.
    pause
    exit /b 1
)

echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak >nul

echo 🎉 EduNerve Platform Started!
echo ================================
echo 📍 Service URLs:
echo    🚪 API Gateway:        http://localhost:8000
echo    🔐 Auth Service:       http://localhost:8001
echo    📚 Content Service:    http://localhost:8002
echo    🤖 Assistant Service:  http://localhost:8003
echo    👨‍💼 Admin Service:       http://localhost:8004
echo    💬 Sync Service:       http://localhost:8005
echo    📁 File Service:       http://localhost:8006
echo    📢 Notification:       http://localhost:8007
echo.
echo 📖 API Documentation:
echo    🚪 API Gateway Docs:   http://localhost:8000/docs
echo    🔐 Auth API Docs:      http://localhost:8001/docs
echo.
echo ℹ️  Frontend: Run separately on your development machine
echo.
echo 🗄️  Database ^& Cache:
echo    🐘 PostgreSQL:        localhost:5432 (edunerve/edunerve2024)
echo    🔴 Redis:             localhost:6379
echo.
echo 📊 Container Status:
docker-compose ps

echo.
echo 📝 Useful Commands:
echo    View logs:           docker-compose logs -f [service-name]
echo    Stop services:       docker-compose down
echo    Restart service:     docker-compose restart [service-name]
echo    Shell into service:  docker-compose exec [service-name] /bin/bash
echo.
echo 🔍 To monitor logs in real-time:
echo    docker-compose logs -f

pause
