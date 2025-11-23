#!/bin/bash

# BrandMind AI - Backend Startup Script
# Starts the FastAPI server with uvicorn

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found at ./venv"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found"
    echo "Create .env with required environment variables"
fi

# Start FastAPI server
echo "Starting BrandMind AI Backend Server..."
echo "API Documentation: http://localhost:8080/docs"
echo "Health Check: http://localhost:8080/health"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8080 --reload
