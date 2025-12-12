@echo off
REM Frontend launcher for development

title Logistics Routing System - Frontend
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Logistics Route Planner Frontend
echo ========================================
echo.

cd frontend

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo Installing frontend dependencies...
call npm install

echo.
echo ========================================
echo   Starting Frontend (Ctrl+C to stop)
echo ========================================
echo Frontend will run on: http://localhost:5173
echo.

REM Start frontend
call npm run dev

pause