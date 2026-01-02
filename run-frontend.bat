@echo off
REM Start frontend in development mode (Windows)

cd /d "%~dp0frontend"
if %errorlevel% neq 0 (
    echo [ERROR] Cannot access frontend directory
    pause
    exit /b 1
)

call npm run electron:dev

pause

