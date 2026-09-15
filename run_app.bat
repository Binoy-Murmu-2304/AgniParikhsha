@echo off
echo ===================================================
echo 🚀 Launching AGNI_PARIKSHA 3.0 (Backend & Frontend)
echo ===================================================
echo.

IF NOT EXIST "dashboard\node_modules" (
    echo Installing dashboard dependencies (npm install)...
    cd dashboard
    call npm install
    cd ..
)

start "AGNI_PARIKSHA Backend Server" cmd /k "python server.py"
start "AGNI_PARIKSHA Frontend Dashboard" cmd /k "cd dashboard && npm run dev"

echo Both Backend (Port 8000) and Frontend (Port 3000) are starting...
echo Open http://localhost:3000 in your browser.
echo.
