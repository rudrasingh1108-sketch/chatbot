@echo off
title Chatbot Launcher
cd /d "%~dp0"
python gui_launcher.py
if errorlevel 1 (
    echo.
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
)
