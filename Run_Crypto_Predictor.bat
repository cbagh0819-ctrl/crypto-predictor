@echo off
title Crypto Watchlist Predictor
cd /d "%~dp0"

echo ==================================================
echo    Launching AI Crypto 24h Growth Predictor
echo ==================================================
echo Starting server and loading live market predictions...

:: Start browser after 2 seconds in background
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"

:: Run the web server
.\.venv\Scripts\python.exe main.py --ui --port 8000

pause
