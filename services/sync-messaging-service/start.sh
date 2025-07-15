#!/bin/bash
echo "Starting EduNerve Sync & Messaging Service..."
echo

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

# Start the service
echo "Starting Sync & Messaging Service on http://localhost:8004..."
echo "WebSocket available at ws://localhost:8004/ws"
echo
echo "Press Ctrl+C to stop the service"
echo
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
