#!/bin/bash
# Backend launcher (Linux/Mac)

echo ""
echo "========================================"
echo "  Logistics Route Planner Backend"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    exit 1
fi

echo "Installing Python dependencies..."
pip3 install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "  Starting Backend (Ctrl+C to stop)"
echo "========================================"
echo "Backend will run on: http://localhost:8000"
echo ""

# Start backend
python3 -m uvicorn app.main:app --reload --port 8000