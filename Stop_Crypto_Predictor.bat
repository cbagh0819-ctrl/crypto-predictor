@echo off
title Stop Crypto Predictor
echo Stopping Crypto Predictor server on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a
)
echo Server stopped.
timeout /t 2 >nul
