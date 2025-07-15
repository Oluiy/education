@echo off
REM EduNerve Project Startup Script for Windows

echo 🚀 Starting EduNerve Platform...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo 📄 Creating .env file from template...
    copy .env.example .env
    echo ✅ .env file created. Please update with your configuration.
)

REM Build and start all services
echo 🔨 Building Docker images...
docker-compose build

echo 🚀 Starting all services...
docker-compose up -d

echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak

echo 🔍 Checking service health...
curl -f http://localhost:8000/health || echo ❌ API Gateway not responding
curl -f http://localhost:8001/health || echo ❌ Auth Service not responding
curl -f http://localhost:8002/health || echo ❌ Content Service not responding

echo ✅ EduNerve Platform is starting up!
echo.
echo 📊 Service URLs:
echo   API Gateway:        http://localhost:8000
echo   Auth Service:       http://localhost:8001
echo   Content Service:    http://localhost:8002
echo   Assistant Service:  http://localhost:8003
echo   Admin Service:      http://localhost:8004
echo   Sync Service:       http://localhost:8005
echo   File Service:       http://localhost:8006
echo   Notification Service: http://localhost:8007
echo   Frontend:           http://localhost:3000
echo   Database:           localhost:5432
echo   Redis:              localhost:6379
echo.
echo 📖 Documentation:
echo   API Gateway:        http://localhost:8000/docs
echo   Auth Service:       http://localhost:8001/docs
echo   Content Service:    http://localhost:8002/docs
echo.
echo 🔧 To stop all services: docker-compose down
echo 🔄 To restart: docker-compose restart
echo 📊 To view logs: docker-compose logs -f
pause
