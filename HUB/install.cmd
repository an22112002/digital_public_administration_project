@echo off
set REDIS_CONTAINER_NAME=HUB-redis-db

set MYSQL_CONTAINER_NAME=HUB-mysql-db

echo Cheking Redis container...

docker ps -a --format "{{.Names}}" | findstr /i /x "%REDIS_CONTAINER_NAME%" >nul

if %errorlevel%==0 (
    echo Redis container exists. Stopping installation.
    pause
    exit /b
)

echo Checking MySQL container...

docker ps -a --format "{{.Names}}" | findstr /i /x "%MYSQL_CONTAINER_NAME%" >nul

if %errorlevel%==0 (
    echo MySQL container exists. Stopping installation.
    pause
    exit /b
)

docker compose up -d

@REM còn cần thêm container cho HUB-frontend và HUB-backend nữa
echo Installation completed.
pause