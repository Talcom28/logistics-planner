#!/bin/bash
# Logistics Routing System - Docker Launcher (Linux/Mac)

echo ""
echo "========================================"
echo "  Logistics Route Planner"
echo "  Starting Application..."
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo ""
    echo "Please install Docker from:"
    echo "https://www.docker.com/products/docker-desktop"
    echo ""
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: docker-compose is not available"
    exit 1
fi

# Start Docker services
echo "Starting Docker services..."
echo ""
docker-compose up

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start services"
    exit 1
fi