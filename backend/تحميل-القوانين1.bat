@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Loading laws into the database, please wait...
echo(
python add_laws_web.py
echo(
echo ==== DONE - copy the result lines above and send them to Claude ====
pause
