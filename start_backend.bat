@echo off
title Antigravity Backend
echo.
echo  =============================================
echo   ANTIGRAVITY CAREER AGENT — Backend Server
echo  =============================================
echo.
echo  Starting FastAPI on http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo.
cd /d "%~dp0"
py -3 -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0
pause
