@echo off
REM Start frontend in browser (Windows)
REM This runs the Vite dev server and lets you open your preferred browser manually.

cd /d "%~dp0frontend"
if %errorlevel% neq 0 (
    echo [ERROR] Cannot access frontend directory
    pause
    exit /b 1
)

call npm run dev

pause

