@echo off
REM Logistics Routing System - Docker Launcher
REM Windows batch file to start the entire application

title Logistics Routing System
echo.
echo ========================================
echo   Logistics Route Planner
echo   Starting Application...
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Docker is not installed or not in PATH
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: docker-compose is not available
    echo.
    pause
    exit /b 1
)

REM Start Docker services
echo Starting Docker services...
echo.
docker-compose up

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start services
    echo.
    pause
    exit /b 1
)