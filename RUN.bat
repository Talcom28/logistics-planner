@echo off
REM Logistics Routing System - Smart Launcher
REM Auto-detects available options and starts the app

cls
title Logistics Route Planner - Setup

echo.
echo ============================================
echo    LOGISTICS ROUTE PLANNER
echo ============================================
echo.

REM Check if Docker is available
docker --version >nul 2>&1
set docker_available=%errorlevel%

REM Check if Python is available
python --version >nul 2>&1
set python_available=%errorlevel%

REM Check if Node is available
node --version >nul 2>&1
set node_available=%errorlevel%

echo Available startup options:
echo.

if %docker_available% equ 0 (
    echo [1] DOCKER (Recommended - Easiest)
    echo     - Starts everything automatically
    echo     - No setup needed
    echo.
)

if %python_available% equ 0 (
    if %node_available% equ 0 (
        echo [2] MANUAL (Backend + Frontend)
        echo     - Requires Node.js (detected)
        echo.
    )
)

if %docker_available% neq 0 (
    if %python_available% neq 0 (
        echo.
        echo ERROR: No suitable startup method found
        echo.
        echo Please install one of:
        echo - Docker Desktop: https://www.docker.com/products/docker-desktop
        echo - Python 3.11 + Node.js: https://python.org + https://nodejs.org
        echo.
        pause
        exit /b 1
    )
)

echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    if %docker_available% equ 0 (
        echo.
        echo Starting Docker services...
        echo Waiting for services to start (this may take 30 seconds)...
        echo.
        docker-compose up
        if errorlevel 1 (
            echo.
            echo ERROR: Failed to start Docker services
            pause
            exit /b 1
        )
    ) else (
        echo Docker not available
        pause
        exit /b 1
    )
) else if "%choice%"=="2" (
    if %python_available% neq 0 (
        echo Python not available
        pause
        exit /b 1
    )
    
    echo.
    echo Installing dependencies...
    pip install -q -r requirements.txt
    
    echo.
    echo Starting Backend on http://localhost:8000
    echo (Keep this window open)
    echo.
    
    start "Frontend" cmd /c "cd frontend && npm install && npm run dev"
    
    echo Waiting 5 seconds before starting backend...
    timeout /t 5 /nobreak
    
    uvicorn app.main:app --reload --port 8000
) else (
    echo Invalid choice
    pause
    exit /b 1
)