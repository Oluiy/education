#!/bin/bash
echo "Starting EduNerve File Storage Service..."
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
echo "Starting File Storage Service on http://localhost:8005..."
echo
echo "Press Ctrl+C to stop the service"
echo
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
