#!/bin/bash
# Frontend launcher (Linux/Mac)

echo ""
echo "========================================"
echo "  Logistics Route Planner Frontend"
echo "========================================"
echo ""

cd frontend

# Check Node
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Download from: https://nodejs.org/"
    exit 1
fi

echo "Installing frontend dependencies..."
npm install

echo ""
echo "========================================"
echo "  Starting Frontend (Ctrl+C to stop)"
echo "========================================"
echo "Frontend will run on: http://localhost:5173"
echo ""

# Start frontend
npm run dev