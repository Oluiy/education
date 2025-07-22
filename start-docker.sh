#!/bin/bash
# ==============================================================================
# EduNerve Docker Setup and Startup Script
# ==============================================================================

echo "🚀 EduNerve Docker Setup & Startup"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker is running"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual configuration before running the services"
    echo "   Key items to configure:"
    echo "   - OPENAI_API_KEY=your-actual-openai-key"
    echo "   - WHATSAPP_API_KEY=your-actual-whatsapp-key"
    echo "   - TWILIO_ACCOUNT_SID=your-actual-twilio-sid"
    echo "   - TWILIO_AUTH_TOKEN=your-actual-twilio-token"
    echo "   - SMTP_USER=your-email@gmail.com"
    echo "   - SMTP_PASSWORD=your-email-password"
    echo "   - JWT_SECRET=your-production-jwt-secret"
    echo ""
    read -p "Press Enter to continue with default values, or Ctrl+C to exit and configure .env first..."
fi

echo "🔧 Preparing Docker environment..."

# Create necessary directories
mkdir -p uploads
mkdir -p data/postgres
mkdir -p data/redis

# Set proper permissions
chmod 755 uploads
chmod 755 data

echo "🧹 Cleaning up previous containers (if any)..."
docker-compose down -v 2>/dev/null || true

echo "🏗️  Building Docker images..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed. Please check the error messages above."
    exit 1
fi

echo "🚀 Starting EduNerve services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services. Please check the error messages above."
    exit 1
fi

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

services=("api-gateway:8000" "auth-service:8001" "content-quiz-service:8002" "assistant-service:8003" "admin-service:8004" "sync-messaging-service:8005" "file-storage-service:8006" "notification-service:8007")

for service in "${services[@]}"; do
    name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    echo -n "  Checking $name... "
    
    # Wait up to 60 seconds for service to be ready
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -sf "http://localhost:$port/health" > /dev/null 2>&1 || curl -sf "http://localhost:$port/docs" > /dev/null 2>&1; then
            echo "✅ Ready"
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        echo "⚠️  Not responding (may still be starting up)"
    fi
done

echo ""
echo "🎉 EduNerve Platform Started!"
echo "================================"
echo "📍 Service URLs:"
echo "   🚪 API Gateway:        http://localhost:8000"
echo "   🔐 Auth Service:       http://localhost:8001"
echo "   📚 Content Service:    http://localhost:8002"
echo "   🤖 Assistant Service:  http://localhost:8003"
echo "   👨‍💼 Admin Service:       http://localhost:8004"
echo "   💬 Sync Service:       http://localhost:8005"
echo "   📁 File Service:       http://localhost:8006"
echo "   📢 Notification:       http://localhost:8007"
echo ""
echo "📖 API Documentation:"
echo "   🚪 API Gateway Docs:   http://localhost:8000/docs"
echo "   🔐 Auth API Docs:      http://localhost:8001/docs"
echo ""
echo "ℹ️  Frontend: Run separately on your development machine"
echo ""
echo "🗄️  Database & Cache:"
echo "   🐘 PostgreSQL:        localhost:5432 (edunerve/edunerve2024)"
echo "   🔴 Redis:             localhost:6379"
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "📝 Useful Commands:"
echo "   View logs:           docker-compose logs -f [service-name]"
echo "   Stop services:       docker-compose down"
echo "   Restart service:     docker-compose restart [service-name]"
echo "   Shell into service:  docker-compose exec [service-name] /bin/bash"
echo ""
echo "🔍 To monitor logs in real-time:"
echo "   docker-compose logs -f"
