#!/bin/bash
# EduNerve API Gateway - Linux/Mac Start Script

echo "🌐 Starting EduNerve API Gateway..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if Redis is available
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️ Redis is not installed. Please install Redis first."
    echo "  Ubuntu/Debian: sudo apt-get install redis-server"
    echo "  macOS: brew install redis"
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping &> /dev/null; then
    echo "⚠️ Redis is not running. Starting Redis..."
    redis-server --daemonize yes
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please configure it with your settings."
fi

# Start the API Gateway
echo "🚀 Starting API Gateway server..."
python main.py
