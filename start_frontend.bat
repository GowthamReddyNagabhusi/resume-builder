@echo off
title CareerForge Frontend
echo.
echo  =============================================
echo   CAREERFORGE — Frontend
echo  =============================================
echo.
echo  Starting Next.js on http://localhost:3000
echo  Make sure backend is running on port 8000!
echo.
cd /d "%~dp0frontend"
npm run dev
pause
