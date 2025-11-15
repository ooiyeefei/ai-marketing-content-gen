#!/bin/bash
# Simple bash script to test locally (alternative to Python script)

set -e

echo "======================================"
echo "  Social Media AI Agency - Local Test"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Cleanup function
cleanup() {
    echo ""
    echo -e "${CYAN}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Check prerequisites
echo -e "${BLUE}→ Checking prerequisites...${NC}"
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}✗ Python 3 not found${NC}"; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}✗ Node.js not found${NC}"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}✗ npm not found${NC}"; exit 1; }
echo -e "${GREEN}✓ All prerequisites found${NC}"
echo ""

# Install backend dependencies
echo -e "${BLUE}→ Installing backend dependencies...${NC}"
cd backend

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo -e "${CYAN}  Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Use venv pip to install dependencies
echo -e "${CYAN}  Installing packages in virtual environment...${NC}"
venv/bin/pip install -q -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"
echo ""

# Install frontend dependencies
echo -e "${BLUE}→ Checking frontend dependencies...${NC}"
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo -e "${CYAN}  Installing Node packages (this may take a few minutes)...${NC}"
    npm install
else
    echo -e "${GREEN}✓ node_modules already exists${NC}"
fi
echo ""

# Start backend
echo -e "${BLUE}→ Starting backend server (port 8080)...${NC}"
cd ../backend
venv/bin/python main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${CYAN}  Backend PID: $BACKEND_PID${NC}"

# Wait for backend
echo -e "${BLUE}→ Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8080/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready!${NC}"
        break
    fi
    sleep 1
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}✗ Backend crashed on startup${NC}"
        cat /tmp/backend.log
        exit 1
    fi
done
echo ""

# Start frontend
echo -e "${BLUE}→ Starting frontend server (port 3000)...${NC}"
cd ../frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${CYAN}  Frontend PID: $FRONTEND_PID${NC}"

# Wait for frontend
echo -e "${BLUE}→ Waiting for frontend to start (this takes longer)...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is ready!${NC}"
        break
    fi
    sleep 1
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}✗ Frontend crashed on startup${NC}"
        cat /tmp/frontend.log
        exit 1
    fi
    if [ $((i % 10)) -eq 0 ]; then
        echo -e "${CYAN}  Still waiting... ($i/60s)${NC}"
    fi
done
echo ""

# Success!
echo "======================================"
echo "  🎉 All Systems Running!"
echo "======================================"
echo ""
echo -e "${GREEN}Frontend URL:${NC}  http://localhost:3000"
echo -e "${GREEN}Backend URL:${NC}   http://localhost:8080"
echo -e "${GREEN}Backend Docs:${NC}  http://localhost:8080/docs"
echo ""
echo -e "${CYAN}Test the API:${NC}"
echo "  curl http://localhost:8080/"
echo ""
echo -e "${CYAN}Stop servers:${NC}"
echo "  Press Ctrl+C"
echo ""
echo -e "${RED}Note:${NC} Without GCP credentials, you'll see fallback data."
echo "      See docs/LOCAL_TESTING_GUIDE.md for full testing."
echo ""

# Try to open browser (macOS/Linux)
if command -v open >/dev/null 2>&1; then
    open http://localhost:3000 2>/dev/null || true
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:3000 2>/dev/null || true
fi

# Show logs
echo "======================================"
echo "  Server Logs (Ctrl+C to stop)"
echo "======================================"
echo ""

tail -f /tmp/backend.log /tmp/frontend.log
