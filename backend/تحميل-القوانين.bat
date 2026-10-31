@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================================
echo   Loading Egyptian laws into legal_ai.db ... please wait
echo ========================================================
echo.
where python >nul 2>nul && (python add_laws_web.py) || (py add_laws_web.py)
echo.
echo ========================================================
echo   DONE. Copy the lines above (the ✅ lines) and send
echo   them to Claude in the chat.
echo ========================================================
echo.
pause
