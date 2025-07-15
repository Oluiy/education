#!/bin/bash
echo "Starting EduNerve Notification Service..."
echo "====================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH=$(pwd)
export PORT=8006

# Start the service
echo "Starting service on port $PORT..."
echo "Service will be available at http://localhost:$PORT"
echo "API documentation at http://localhost:$PORT/docs"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

cd app
python -m uvicorn main:app --host 0.0.0.0 --port $PORT --reload
