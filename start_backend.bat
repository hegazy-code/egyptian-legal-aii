@echo off
REM ============================================================
REM  Egyptian Legal AI -- Backend launcher (Windows)
REM  Double-click this file to set up and run the FastAPI backend.
REM ============================================================
cd /d "%~dp0backend"

if not exist ".env" (
    echo Creating backend\.env from .env.example ...
    copy ".env.example" ".env" >nul
    echo.
    echo A Notepad window will open so you can paste your GEMINI_API_KEY.
    echo Get a free key at: https://aistudio.google.com/apikey
    echo Also set JWT_SECRET to any random string of your choosing.
    echo SAVE the file and CLOSE Notepad to continue.
    echo.
    pause
    notepad ".env"
)

if not exist "venv\" (
    echo Creating Python virtual environment ...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies (first run only, this can take a few minutes) ...
pip install -r requirements.txt

echo Applying database migrations ...
alembic upgrade head

echo.
echo ============================================================
echo  Starting backend at http://localhost:8000
echo  Leave this window open while you use the app.
echo  Press CTRL+C here to stop the server.
echo ============================================================
echo.
uvicorn app.main:app --reload

pause
