#!/bin/bash

echo "Starting EduNerve Assistant Service..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create .env file with required configuration"
    echo "See README.md for details"
    read -p "Press Enter to continue anyway..."
fi

# Create audio directory if it doesn't exist
if [ ! -d "audio_files" ]; then
    mkdir audio_files
    echo "Created audio_files directory"
fi

# Start the service
echo "Starting Assistant Service on port 8003..."
echo "Press Ctrl+C to stop the service"
echo ""
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
