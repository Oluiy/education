#!/bin/bash
# Rebuild and start all services with fixes

echo "🔧 Stopping all containers..."
docker-compose down

echo "🧹 Cleaning up..."
docker system prune -f

echo "🔨 Building all services..."
docker-compose build --no-cache

echo "🚀 Starting services with health checks..."
docker-compose up -d

echo "📊 Checking service status..."
sleep 10
docker-compose ps

echo "📝 Checking logs for errors..."
docker-compose logs --tail=20
