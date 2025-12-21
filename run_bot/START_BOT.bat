@echo off
title BinanceBot - Crypto Trading Bot
color 0A

:: Navigate to project root (parent of run_bot folder)
cd /d "%~dp0.."

echo ========================================
echo    BinanceBot - Starting Services
echo ========================================
echo.

:: Check if config.json exists
if not exist "config\config.json" (
    echo [0/4] Initializing config.json from template...
    if exist "config\config.json.example" (
        copy "config\config.json.example" "config\config.json" >nul
        echo Please edit config/config.json with your API keys before running again!
        pause
        exit /b 1
    ) else (
        echo ERROR: config.json.example not found!
        pause
        exit /b 1
    )
)

echo [1/4] Cleaning up existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
timeout /t 1 /nobreak >nul

echo [2/4] Starting Backend (Port 8080)...
:: Run from project root so user_data and data folders are found correctly
set PYTHONPATH=%cd%\backend
start "BinanceBot Backend" cmd /k "cd /d %cd% && python -m binancebot.main trade --config config\config.json"
timeout /t 3 /nobreak >nul

echo [3/4] Waiting for Backend to initialize...
timeout /t 5 /nobreak >nul

echo [4/4] Starting Frontend (Web UI)...
start "BinanceBot Frontend" cmd /k "cd /d %cd%\frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    All services started successfully!
echo ========================================
echo.
echo    Backend:  http://localhost:8080
echo    Frontend: http://localhost:3000
echo.
echo    Opening browser...
echo ========================================

start http://localhost:3000

echo.
echo Press any key to close this window...
echo (Backend and Frontend will continue running)
pause >nul
