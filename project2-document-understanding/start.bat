@echo off
setlocal
cd /d "%~dp0"
title Document Assistant - Launcher
set PORT=5002

echo ==================================================
echo   Document Understanding Assistant - starting
echo ==================================================

where python >nul 2>nul
if errorlevel 1 goto nopython

if exist ".venv\Scripts\python.exe" goto havevenv
echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 goto venvfail

:havevenv
echo Installing dependencies. The first run can take a few minutes...
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto pipfail

if not exist "data\eval_docs\index.csv" ".venv\Scripts\python.exe" scripts\generate_data.py
if not exist "models\doctype_model.joblib" ".venv\Scripts\python.exe" scripts\train.py

netstat -aon | findstr ":%PORT% " | findstr LISTENING >nul
if not errorlevel 1 goto already

start "Document Assistant Server" /min cmd /c ".venv\Scripts\python.exe app.py"
echo Waiting for the server to come up...
timeout /t 5 /nobreak >nul
start "" http://127.0.0.1:%PORT%
echo.
echo Document Assistant is running at http://127.0.0.1:%PORT%
echo Use stop.bat to shut it down.
timeout /t 3 >nul
exit /b 0

:already
echo The server is already running on port %PORT%. Opening the browser...
start "" http://127.0.0.1:%PORT%
exit /b 0

:nopython
echo [ERROR] Python was not found. Install Python 3.10 or newer from python.org and tick Add Python to PATH.
pause
exit /b 1

:venvfail
echo [ERROR] Could not create the virtual environment.
pause
exit /b 1

:pipfail
echo [ERROR] Dependency installation failed. Check your internet connection and try again.
pause
exit /b 1
