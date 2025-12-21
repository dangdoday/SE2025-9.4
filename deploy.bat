@echo off
REM Deployment script for Windows
REM Usage: deploy.bat

echo =========================================
echo Deploying BinanceBot
echo =========================================

REM Pull latest code
echo [INFO] Pulling latest code from Git...
git fetch origin
git reset --hard origin/main

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose down

REM Pull latest images
echo [INFO] Pulling latest Docker images...
docker-compose pull

REM Build and start containers
echo [INFO] Building and starting containers...
docker-compose up -d --build --force-recreate

REM Wait for services
echo [INFO] Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Show container status
echo [INFO] Container status:
docker-compose ps

REM Show recent logs
echo [INFO] Recent logs:
docker-compose logs --tail=50

REM Clean up
echo [INFO] Cleaning up old Docker images...
docker system prune -f

echo.
echo =========================================
echo [INFO] Deployment completed successfully!
echo =========================================
echo.
echo Useful commands:
echo   View logs:        docker-compose logs -f
echo   Stop services:    docker-compose down
echo   Restart services: docker-compose restart
echo   View status:      docker-compose ps
echo.
pause
