@echo off
setlocal enabledelayedexpansion
set PORT=5001
set FOUND=0

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%PORT% " ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>nul
    set FOUND=1
)

if "!FOUND!"=="1" (
    echo Support Triage server stopped.
) else (
    echo Support Triage server was not running.
)
timeout /t 2 >nul
