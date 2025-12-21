@echo off
title BinanceBot - Stopping Services
color 0C

cd /d "%~dp0.."

echo ========================================
echo    BinanceBot - Stopping All Services
echo ========================================
echo.

echo [1/2] Stopping Backend and Frontend processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo [2/2] Cleaning up network ports (8080, 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /f /pid %%a 2>nul

echo.
echo ========================================
echo    All services stopped!
echo ========================================
echo.
echo Press any key to close...
pause >nul
