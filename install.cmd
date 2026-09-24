@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

echo [1/4] Checking Docker CLI...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not found in PATH.
    pause
    exit /b 1
)

echo [2/4] Checking Docker Engine...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Engine is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [3/4] Preparing service list...
set SERVICES=mysql redis

echo [4/4] Running Docker Compose for: !SERVICES!
docker compose up -d --build !SERVICES!
if errorlevel 1 (
    echo [ERROR] Deployment failed.
    pause
    exit /b 1
)

echo.
echo Deployment completed successfully.
docker compose ps
pause