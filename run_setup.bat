@echo off
REM Egyptian Legal AI — one-shot setup and launch
REM Double-click this file from the project root to:
REM   1. Run Alembic migrations
REM   2. Seed the database with Egyptian law articles
REM   3. Start the FastAPI backend (hot-reload enabled)

echo ========================================
echo  Egyptian Legal AI — Setup and Launch
echo ========================================

cd /d "%~dp0backend"

echo.
echo [1/3] Running database migrations...
call alembic upgrade head
if %ERRORLEVEL% neq 0 (
    echo ERROR: Alembic migration failed. Is alembic installed?
    pause
    exit /b 1
)
echo Migration complete.

echo.
echo [2/3] Seeding law articles into the database...
cd /d "%~dp0"
python scripts/seed_laws_direct.py --backend-dir backend
if %ERRORLEVEL% neq 0 (
    echo ERROR: Seeding failed. Check scripts/seed_laws_direct.py for details.
    pause
    exit /b 1
)
echo Seeding complete.

echo.
echo [3/3] Starting FastAPI backend on http://localhost:8000 ...
echo       Press Ctrl+C to stop.
cd /d "%~dp0backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
