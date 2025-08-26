@echo off
echo Starting Python Flask Backend...
echo.

echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)
echo.

echo Step 2: Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo.

echo Step 3: Starting Flask backend...
python start_python_server.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to start Flask backend
    pause
    exit /b 1
)
