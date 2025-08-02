@echo off
echo Starting Credit Approval System...
echo ==================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

echo Docker is running
echo Building and starting services...

REM Build and start services
docker-compose up --build -d

echo Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if not errorlevel 1 (
    echo Services are running!
    echo.
    echo Application URLs:
    echo    API Base:        http://localhost:8000/api/
    echo    API Docs:        http://localhost:8000/api/docs/
    echo    Django Admin:    http://localhost:8000/admin/
    echo.
    echo Service Status:
    docker-compose ps
    echo.
    echo To test the API, run:
    echo    python test_api.py
    echo.
    echo To view logs:
    echo    docker-compose logs -f web
    echo    docker-compose logs -f celery
    echo.
    echo To stop services:
    echo    docker-compose down
) else (
    echo Some services failed to start. Check logs:
    echo    docker-compose logs
)

pause
