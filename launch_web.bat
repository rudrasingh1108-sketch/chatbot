@echo off
REM Voice Assistant - Web Application Launcher
REM This script starts the Flask web server

title Voice Assistant - Web App
color 0A

echo.
echo ===================================================
echo    Voice Assistant Web Application
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Check if venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install required packages
echo Installing dependencies...
pip install flask flask-cors numpy speechrecognition pyttsx3 -q

REM Start the web application
echo.
echo ===================================================
echo    Starting Web Server...
echo ===================================================
echo.
echo Web Application: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
