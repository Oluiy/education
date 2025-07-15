#!/bin/bash
echo "🚀 Starting EduNerve Content & Quiz Service"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory
if [ ! -d "uploads" ]; then
    mkdir uploads
    echo "Created uploads directory"
fi

# Run the application
echo ""
echo "Starting FastAPI server..."
echo "API Documentation will be available at: http://localhost:8001/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
