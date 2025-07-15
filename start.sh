#!/bin/bash
# EduNerve Project Startup Script

echo "🚀 Starting EduNerve Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update with your configuration."
fi

# Build and start all services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting all services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🔍 Checking service health..."
curl -f http://localhost:8000/health || echo "❌ API Gateway not responding"
curl -f http://localhost:8001/health || echo "❌ Auth Service not responding"
curl -f http://localhost:8002/health || echo "❌ Content Service not responding"

echo "✅ EduNerve Platform is starting up!"
echo ""
echo "📊 Service URLs:"
echo "  API Gateway:        http://localhost:8000"
echo "  Auth Service:       http://localhost:8001"
echo "  Content Service:    http://localhost:8002"
echo "  Assistant Service:  http://localhost:8003"
echo "  Admin Service:      http://localhost:8004"
echo "  Sync Service:       http://localhost:8005"
echo "  File Service:       http://localhost:8006"
echo "  Notification Service: http://localhost:8007"
echo "  Frontend:           http://localhost:3000"
echo "  Database:           localhost:5432"
echo "  Redis:              localhost:6379"
echo ""
echo "📖 Documentation:"
echo "  API Gateway:        http://localhost:8000/docs"
echo "  Auth Service:       http://localhost:8001/docs"
echo "  Content Service:    http://localhost:8002/docs"
echo ""
echo "🔧 To stop all services: docker-compose down"
echo "🔄 To restart: docker-compose restart"
echo "📊 To view logs: docker-compose logs -f"
