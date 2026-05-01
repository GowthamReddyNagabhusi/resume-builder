@echo off
echo ========================================================
echo       CareerForge - One-Click Live Environment
echo ========================================================
echo.
echo Step 1: Starting Database and Application Containers...
docker-compose up -d --build

echo.
echo Step 2: Waiting for containers to be healthy...
timeout /t 10 /nobreak > NUL

echo.
echo ========================================================
echo   APPLICATION IS RUNNING LOCALLY AT http://localhost:3000
echo ========================================================
echo.
echo Step 3: Exposing application to the public internet...
echo Please copy the address below to share CareerForge live:
echo.

call npx localtunnel --port 3000

pause
