@echo off
echo ========================================================
echo   CareerForge - One-Click Live Environment (No Docker)
echo ========================================================
echo.
echo Step 1: Starting Backend API...
cd backend
start /b uvicorn backend.main:app --host 0.0.0.0 --port 8000
cd ..

echo.
echo Step 2: Starting Frontend...
cd frontend
call npm install
start /b npm run dev
cd ..

echo.
echo Step 3: Waiting for services to start...
timeout /t 10 /nobreak > NUL

echo.
echo ========================================================
echo   APPLICATION IS RUNNING LOCALLY AT http://localhost:3000
echo ========================================================
echo.
echo Step 4: Exposing application to the public internet...
echo Please copy the address below to share CareerForge live.
echo Install localtunnel first if not present: npm install -g localtunnel
echo.

call npx localtunnel --port 3000

pause
