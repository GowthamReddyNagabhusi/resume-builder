@echo off
REM Setup script for local development (Windows)

echo.
echo ================================
echo Resume Builder - Local Setup
echo ================================
echo.

REM Check Docker
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check Docker Compose
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create .env if it doesn't exist
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please edit .env with your configuration
)

REM Create storage directory
if not exist storage mkdir storage

REM Start services
echo.
echo Starting Docker containers...
docker-compose up -d

REM Wait for services
echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak

REM Check service health
echo.
echo Checking service health...

for /f "delims=" %%A in ('curl -s -o NUL -w "%%{http_code}" http://localhost:8000/health 2^>NUL') do set "BACKEND_HEALTH=%%A"
if "%BACKEND_HEALTH%"=="200" (
    echo Backend is healthy: http://localhost:8000
) else (
    echo Warning: Backend health check returned %BACKEND_HEALTH%
)

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Services:
echo   - API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - Frontend: http://localhost:3000
echo   - Database: localhost:5432
echo   - PgAdmin: http://localhost:5050
echo.
echo Next steps:
echo 1. Open http://localhost:3000 in your browser
echo 2. Sign up for an account
echo 3. Start adding career data
echo.
echo To stop services: docker-compose down
echo To view logs: docker-compose logs -f
