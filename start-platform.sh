#!/bin/bash

# EduNerve Platform - Complete Startup Script
# This script builds and starts all services with proper initialization

set -e

echo "🚀 Starting EduNerve Educational Platform..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

print_status "Docker is running and Docker Compose is available"

# Clean up any existing containers
print_status "Cleaning up existing containers..."
docker-compose down -v --remove-orphans 2>/dev/null || true

# Remove any dangling images
print_status "Cleaning up dangling images..."
docker image prune -f

# Build all services
print_status "Building all services..."
docker-compose build --no-cache

# Start infrastructure services first
print_status "Starting infrastructure services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
until docker-compose exec postgres pg_isready -U edunerve -d edunerve; do
    echo "PostgreSQL is not ready yet. Waiting..."
    sleep 2
done
print_success "PostgreSQL is ready"

# Wait for Redis to be ready
print_status "Waiting for Redis to be ready..."
until docker-compose exec redis redis-cli ping | grep PONG; do
    echo "Redis is not ready yet. Waiting..."
    sleep 2
done
print_success "Redis is ready"

# Start backend services
print_status "Starting backend services..."
docker-compose up -d \
    auth-service \
    content-quiz-service \
    file-storage-service \
    sync-messaging-service \
    assistant-service \
    admin-service \
    notification-service

# Wait for services to be healthy
print_status "Waiting for backend services to be ready..."
sleep 10

# Start API Gateway
print_status "Starting API Gateway..."
docker-compose up -d api-gateway

# Wait for API Gateway to be ready
print_status "Waiting for API Gateway to be ready..."
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo "API Gateway is not ready yet. Waiting..."
    sleep 2
done
print_success "API Gateway is ready"

# Install frontend dependencies and build
print_status "Setting up frontend..."
cd frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js and npm."
    exit 1
fi

# Install dependencies
print_status "Installing frontend dependencies..."
npm install

# Build the frontend
print_status "Building frontend application..."
npm run build

# Start the frontend in development mode
print_status "Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

# Go back to root directory
cd ..

# Display service status
echo ""
echo "🎉 EduNerve Platform is now running!"
echo "================================================"
echo ""
echo "📊 Service Status:"
echo "✅ PostgreSQL Database: localhost:5432"
echo "✅ Redis Cache: localhost:6379"
echo "✅ API Gateway: http://localhost:8000"
echo "✅ Frontend Application: http://localhost:3000"
echo ""
echo "🔧 Backend Services:"
echo "  • Auth Service: Port 8001"
echo "  • Content & Quiz Service: Port 8002"
echo "  • File Storage Service: Port 8003"
echo "  • Sync & Messaging Service: Port 8004"
echo "  • AI Assistant Service: Port 8005"
echo "  • Admin Service: Port 8006"
echo "  • Notification Service: Port 8007"
echo ""
echo "📱 Frontend Features Available:"
echo "  • Course Management: http://localhost:3000/dashboard/courses"
echo "  • Quiz System: http://localhost:3000/dashboard/quizzes"
echo "  • Real-time Messaging: http://localhost:3000/dashboard/messages"
echo "  • File Management: http://localhost:3000/dashboard/files"
echo "  • Analytics Dashboard: http://localhost:3000/dashboard/analytics"
echo ""
echo "🔗 API Documentation:"
echo "  • API Gateway: http://localhost:8000/docs"
echo "  • Direct service docs available on individual service ports"
echo ""
echo "💾 Database Access:"
echo "  • Host: localhost"
echo "  • Port: 5432"
echo "  • Database: edunerve"
echo "  • Username: edunerve"
echo "  • Password: edunerve2024"
echo ""
echo "🛑 To stop all services:"
echo "  docker-compose down"
echo "  kill $FRONTEND_PID  # Stop frontend dev server"
echo ""

# Health check all services
print_status "Performing health checks..."
echo ""

# Check API Gateway
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "API Gateway: Healthy"
else
    print_warning "API Gateway: Not responding"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend: Healthy"
else
    print_warning "Frontend: Not ready yet (may still be starting)"
fi

# Check individual services through API Gateway
services=("auth" "content" "files" "sync" "assistant" "admin" "notifications")
for service in "${services[@]}"; do
    if curl -f "http://localhost:8000/api/v1/$service/health" > /dev/null 2>&1; then
        print_success "$service service: Healthy"
    else
        print_warning "$service service: Not responding"
    fi
done

echo ""
print_success "Platform startup complete!"
echo ""
echo "📖 Next Steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Create an admin account or use test credentials"
echo "3. Start creating courses and content"
echo "4. Invite students and teachers"
echo ""
echo "📚 Documentation and API testing:"
echo "• Visit http://localhost:8000/docs for API documentation"
echo "• Use the frontend interface for user-friendly interaction"
echo ""
echo "🎯 Key Features to Test:"
echo "• Create and manage courses"
echo "• Upload and organize course materials"
echo "• Generate AI-powered quizzes"
echo "• Real-time messaging and collaboration"
echo "• Progress tracking and analytics"
echo ""

# Keep script running to show logs
print_status "Monitoring service logs (Ctrl+C to stop)..."
docker-compose logs -f
