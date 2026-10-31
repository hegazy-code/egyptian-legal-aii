@echo off
REM ============================================================
REM  Egyptian Legal AI -- Frontend launcher (Windows)
REM  Double-click this file to set up and run the Next.js frontend.
REM  Run start_backend.bat FIRST, in its own window, and leave it running.
REM ============================================================
cd /d "%~dp0frontend"

if not exist ".env.local" (
    echo Creating frontend\.env.local ...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000> .env.local
)

if not exist "node_modules\" (
    echo Installing dependencies (first run only, this can take a few minutes) ...
    npm install
)

echo.
echo ============================================================
echo  Starting frontend at http://localhost:3000
echo  Leave this window open while you use the app.
echo  Press CTRL+C here to stop the server.
echo ============================================================
echo.
npm run dev

pause
