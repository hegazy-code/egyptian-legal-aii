@echo off
start "backend" cmd /k "cd /d C:\Users\Yousssef\OneDrive\Desktop\egyptian-legal-ai\backend && python -m uvicorn app.main:app --reload --port 8000"
start "frontend" cmd /k "cd /d C:\Users\Yousssef\OneDrive\Desktop\egyptian-legal-ai\frontend && npm run dev"
