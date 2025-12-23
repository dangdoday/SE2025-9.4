@echo off
title BinanceBot - Installation
color 0E

:: Navigate to project root
cd /d "%~dp0.."

echo ========================================
echo    BinanceBot - First Time Setup
echo ========================================
echo.
echo This script will install all required dependencies.
echo Please wait, this may take a few minutes...
echo.

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo [2/4] Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo [3/4] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some Python packages failed to install.
    echo You may need to install TA-Lib manually.
    echo See: https://github.com/cgohlke/talib-build/releases
)

echo.
echo [4/4] Installing Frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo You can now run START_BOT.bat to start the bot.
echo.
echo Default Login:
echo   Username: admin
echo   Password: pass789
echo.
echo IMPORTANT: Edit config/config.json with your Binance API keys!
echo.
echo Press any key to close...
pause >nul
