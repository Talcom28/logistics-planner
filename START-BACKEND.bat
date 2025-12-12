@echo off
REM Logistics Routing System - Manual Setup Launcher
REM For development without Docker

title Logistics Routing System - Manual Setup
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Logistics Route Planner
echo   Manual Setup Mode
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Starting Backend (Ctrl+C to stop)
echo ========================================
echo Backend will run on: http://localhost:8000
echo.

REM Start backend
uvicorn app.main:app --reload --port 8000

pause