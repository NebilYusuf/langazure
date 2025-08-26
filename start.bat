@echo off
echo Starting Document Upload & Viewer with Python Flask Backend...
echo.

echo Step 1: Starting Python Flask Backend...
start "Python Backend" cmd /k "cd server && start_python.bat"

echo Step 2: Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Step 3: Starting Frontend Application...
start "Frontend App" cmd /k "npm start"

echo.
echo Both servers are starting...
echo Python Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul
