@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM Start backend server using uv (Windows)

REM Usage:
REM   run-backend.bat dev
REM   run-backend.bat development
REM   run-backend.bat

REM Get script directory (project root)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "BACKEND_DIR=%PROJECT_ROOT%backend"

REM Add project root to PATH so the script can be rerun from subdirectories
REM (e.g., after `cd backend`) in the same terminal session.
set "UPDATED_PATH=%PROJECT_ROOT%;%PATH%"

REM Parse optional dev mode parameter
set "DEV_MODE=0"
if /I "%~1"=="dev" set "DEV_MODE=1"
if /I "%~1"=="development" set "DEV_MODE=1"
if /I "%~1"=="--dev" set "DEV_MODE=1"
if /I "%~1"=="--development" set "DEV_MODE=1"

REM Change to backend directory
pushd "%BACKEND_DIR%"
if %errorlevel% neq 0 (
    echo [ERROR] Cannot access backend directory: %BACKEND_DIR%
    goto :cleanup_fail
)

REM Unset VIRTUAL_ENV if it points to a different location (e.g., root .venv)
REM This ensures uv uses the backend\.venv instead
if defined VIRTUAL_ENV (
    set "CURRENT_VENV=%CD%\.venv"
    if not "%VIRTUAL_ENV%"=="%CURRENT_VENV%" (
        echo [INFO] Unsetting VIRTUAL_ENV to use backend\.venv
        set "VIRTUAL_ENV="
    )
)

REM Check if uv is available
where uv >nul 2>&1
if %errorlevel% equ 0 (
    echo [START] Starting Babblr backend with uv...
    echo    Working directory: %CD%
    echo    Virtual environment: %CD%\.venv
    if "%DEV_MODE%"=="1" (
        echo    Mode: development (auto-reload on changes)
    ) else (
        echo    Mode: production
    )

    REM Ensure .venv exists in backend directory
    if not exist ".venv" (
        echo [WARNING] Virtual environment not found. Creating .venv in backend directory...
        uv venv
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to create virtual environment
            pause
            exit /b 1
        )
    )

    REM Set PYTHONPATH to backend directory
    set "PYTHONPATH=%CD%"

    REM Ensure .env is loaded from backend directory
    if exist ".env" (
        echo    Using .env from: %CD%\.env
    ) else (
        echo [WARNING] .env file not found in backend directory
    )

    REM Run the server
    if "%DEV_MODE%"=="1" (
        REM Dev mode: use uvicorn CLI directly for reliable reload
        REM Read host/port from env or use defaults matching config.py
        if not defined BABBLR_API_HOST set "BABBLR_API_HOST=127.0.0.1"
        if not defined BABBLR_API_PORT set "BABBLR_API_PORT=8000"
        uv run uvicorn app.main:app --reload --host %BABBLR_API_HOST% --port %BABBLR_API_PORT%
    ) else (
        REM Production mode: use the entry point (no reload)
        uv run babblr-backend
    )
) else (
    echo [WARNING] uv not found, falling back to standard Python...
    echo    For better performance, install uv: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

    REM Fallback: manually activate venv if it exists
    if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
    ) else if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    )

    set "PYTHONPATH=%CD%"
    if "%DEV_MODE%"=="1" (
        REM Dev mode: use uvicorn CLI directly for reliable reload
        if not defined BABBLR_API_HOST set "BABBLR_API_HOST=127.0.0.1"
        if not defined BABBLR_API_PORT set "BABBLR_API_PORT=8000"
        python -m uvicorn app.main:app --reload --host %BABBLR_API_HOST% --port %BABBLR_API_PORT%
    ) else (
        REM Production mode
        cd app
        python main.py
    )
)

:cleanup_ok
popd
pause
endlocal & set "PATH=%UPDATED_PATH%"
exit /b 0

:cleanup_fail
popd
pause
endlocal & set "PATH=%UPDATED_PATH%"
exit /b 1

