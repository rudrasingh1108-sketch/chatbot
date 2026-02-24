@echo off
title Chatbot Setup
color 0A
cls

echo.
echo ========================================
echo    AI Voice Chatbot - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo Important: Check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/3] Python found!
python --version
echo.

echo [2/3] Installing dependencies...
echo This may take a few minutes...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Error: Failed to install dependencies
    echo Try running: pip install --upgrade pip
    pause
    exit /b 1
)

echo.
echo [3/3] Setup complete!
echo.
echo ========================================
echo    Setup Successful!
echo ========================================
echo.
echo Next steps:
echo 1. Get News API Key (optional):
echo    - Visit: https://newsapi.org/
echo    - Sign up and get free API key
echo    - Add it in the GUI Launcher settings
echo.
echo 2. Start the Chatbot:
echo    - Option A: Run launch.bat
echo    - Option B: Run: python gui_launcher.py
echo    - Option C: Run: python main.py
echo.
echo 3. Say "Hey Assistant" to activate
echo.
pause
